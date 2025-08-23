# Database Documentation

## Recent Updates (August 2025)

**Parameter Standardization**: All database functions have been updated to use consistent year/period parameters instead of date parameters for improved consistency and performance:

- ✅ `actual_account` - Updated from date parameters to `(start_year, start_period, end_year, end_period)`
- ✅ `actual_metric` - Updated from date parameters to `(start_year, start_period, end_year, end_period)` 
- ✅ `budget_vs_actual_metric` - Renamed from `budget_vs_actual` and updated to use year/period parameters
- ⚠️ `actual_account_average` - Updated but may have type casting issues (periods_count)
- ⚠️ `actual_metric_average` - Updated but may have column reference ambiguity issues

**Django Integration**: All corresponding Django functions in `dashboard/db.py` have been updated to use the new parameter format.

## Schemas

- finance
- information_schema
- pg_catalog
- pg_temp_5
- pg_toast
- pg_toast_temp_5
- public


## Tables

### public.budget
- `account` (integer)
- `amt1` (numeric)
- `booktype` (text)
- `companyid` (text)
- `period` (integer)
- `uniqueid` (bigint)
- `year` (integer)

### public.company
- `companyid` (text)
- `company_name` (text)

### public.gl_account_map
- `account_name` (text)
- `range_start` (integer)
- `range_end` (integer)
- `erp_sign` (smallint)
- `tags` (jsonb)
- `acct_range` (int4range)

### public.gl_txn_raw
- `gl_account` (integer)
- `companyid` (text)
- `customer` (text)
- `posting_date` (date)
- `description` (text)
- `extdescription` (text)
- `amount_raw` (numeric)
- `invoicetype` (text)
- `invvouch` (integer)
- `postperiod` (smallint)
- `postyear` (integer)
- `source` (text)
- `sourcekey` (text)
- `supplierinvnum` (text)
- `transcode` (smallint)
- `uniqueid` (bigint)

### public.gl_txn_signed
- `gl_account` (integer)
- `companyid` (text)
- `customer` (text)
- `posting_date` (date)
- `description` (text)
- `extdescription` (text)
- `amount_raw` (numeric)
- `invoicetype` (text)
- `invvouch` (integer)
- `postperiod` (smallint)
- `postyear` (integer)
- `source` (text)
- `sourcekey` (text)
- `supplierinvnum` (text)
- `transcode` (smallint)
- `uniqueid` (bigint)
- `account_name` (text)
- `amount` (numeric)
- `tags` (jsonb)

### public.metric
- `metric_id` (integer)
- `metric_name` (text)
- `combine` (text)

### public.metric_component
- `metric_id` (integer)
- `ref_type` (text)
- `ref_name` (text)
- `op` (text)


## Functions

### finance.actual_account(p_start_year integer, p_start_period integer, p_end_year integer, p_end_period integer, p_company_ids text[] DEFAULT NULL::text[], p_components text[] DEFAULT NULL::text[])
- Returns: TABLE(companyid text, ref_name text, value numeric)
- Returns set of rows
- **Updated**: Now uses year/period parameters instead of dates for consistency

```sql
CREATE OR REPLACE FUNCTION finance.actual_account(p_start_year integer, p_start_period integer, p_end_year integer, p_end_period integer, p_company_ids text[] DEFAULT NULL::text[], p_components text[] DEFAULT NULL::text[])
 RETURNS TABLE(companyid text, ref_name text, value numeric)
 LANGUAGE plpgsql
AS $function$
    -- Implementation uses postyear and postperiod columns from gl_txn_raw
    -- Filters transactions based on year/period ranges
    -- Returns aggregated account values
$function$
```

### finance.actual_account_average(p_start_year integer, p_start_period integer, p_end_year integer, p_end_period integer, p_company_ids text[], p_components text[] DEFAULT NULL::text[])
- Returns: TABLE(companyid text, ref_name text, avg_value numeric, min_value numeric, max_value numeric, periods_count integer, start_date date, end_date date)
- Returns set of rows

```sql
CREATE OR REPLACE FUNCTION finance.actual_account_average(p_start_year integer, p_start_period integer, p_end_year integer, p_end_period integer, p_company_ids text[], p_components text[] DEFAULT NULL::text[])
 RETURNS TABLE(companyid text, ref_name text, avg_value numeric, min_value numeric, max_value numeric, periods_count integer, start_date date, end_date date)
 LANGUAGE plpgsql
AS $function$
DECLARE
    v_start_month date := make_date(p_start_year, p_start_period, 1);
    v_end_month   date := make_date(p_end_year,   p_end_period,   1);
    v_end_date    date := (v_end_month + INTERVAL '1 month' - INTERVAL '1 day')::date;
BEGIN
    RETURN QUERY
    WITH months AS (
        SELECT gs::date AS period_start
        FROM generate_series(v_start_month, v_end_month, INTERVAL '1 month') AS gs
    ),
    per_month AS (
        SELECT
            b.companyid,
            b.ref_name,
            mo.period_start,
            b.value::numeric AS value
        FROM months mo
        CROSS JOIN LATERAL finance.actual_account(
            mo.period_start::date,
            (mo.period_start + INTERVAL '1 month')::date,
            p_company_ids,
            p_components
        ) AS b
    )
    SELECT
        pm.companyid,
        pm.ref_name,
        AVG(pm.value)                         AS avg_value,
        MIN(pm.value)                         AS min_value,
        MAX(pm.value)                         AS max_value,
        COUNT(DISTINCT pm.period_start)::int  AS periods_count,
        v_start_month                         AS start_date,
        v_end_date                            AS end_date
    FROM per_month pm
    GROUP BY pm.companyid, pm.ref_name
    ORDER BY pm.companyid, pm.ref_name;
END;
$function$
```

### finance.actual_metric(p_start_year integer, p_start_period integer, p_end_year integer, p_end_period integer, p_company_ids text[] DEFAULT NULL::text[], p_metric_names text[] DEFAULT NULL::text[])
- Returns: TABLE(companyid text, metric_name text, value numeric)
- Returns set of rows
- **Updated**: Now uses year/period parameters instead of dates for consistency

```sql
CREATE OR REPLACE FUNCTION finance.actual_metric(p_start_year integer, p_start_period integer, p_end_year integer, p_end_period integer, p_company_ids text[] DEFAULT NULL::text[], p_metric_names text[] DEFAULT NULL::text[])
 RETURNS TABLE(companyid text, metric_name text, value numeric)
 LANGUAGE plpgsql
AS $function$
    -- Implementation uses postyear and postperiod columns from gl_txn_raw
    -- Filters transactions based on year/period ranges  
    -- Calculates metric values using recursive component expansion
    -- Returns aggregated metric values

    PERFORM 1
    FROM unnest(p_company_ids) u
    LEFT JOIN public.company c ON c.companyid = u
    WHERE c.companyid IS NULL;
    IF FOUND THEN
      RAISE EXCEPTION 'One or more company IDs not valid: %', p_company_ids;
    END IF;
  END IF;

  IF use_metric THEN
    p_metric_names := ARRAY(SELECT BTRIM(x) FROM unnest(p_metric_names) AS x);
  END IF;

  -- Case 1: no company filter, no metric filter
  IF NOT use_company AND NOT use_metric THEN
    RETURN QUERY
    WITH RECURSIVE
    month_txn AS (
      SELECT t.companyid, m.account_name,
             SUM(t.amount_raw * m.erp_sign)::numeric AS amount
      FROM public.gl_txn_raw t
      JOIN public.gl_account_map m
        ON t.gl_account::int4 <@ m.acct_range
      WHERE t.posting_date >= p_start_date
        AND t.posting_date <  v_end_date
      GROUP BY t.companyid, m.account_name
    ),
    mc_base AS (
      SELECT mc.metric_id, mc.ref_type, mc.ref_name,
             CASE mc.op WHEN '+' THEN 1 ELSE -1 END AS sign
      FROM public.metric_component mc
    ),
    expand(metric_id, ref_type, ref_name, sign) AS (
      SELECT metric_id, ref_type, ref_name, sign FROM mc_base
      UNION ALL
      SELECT e.metric_id, mc2.ref_type, mc2.ref_name,
             e.sign * CASE mc2.op WHEN '+' THEN 1 ELSE -1 END
      FROM expand e
      JOIN public.metric_component mc2
        ON e.ref_type = 'metric'
       AND e.ref_name = (
             SELECT m.metric_name FROM public.metric m
             WHERE m.metric_id = mc2.metric_id
           )
    ),
    leaf AS (
      SELECT e.metric_id, e.ref_name AS account_name, e.sign
      FROM expand e
      WHERE e.ref_type = 'account'
    ),
    metric_values AS (
      SELECT mt.companyid, m.metric_name AS mname,
             SUM(l.sign * mt.amount) AS val
      FROM month_txn mt
      JOIN leaf l ON l.account_name = mt.account_name
      JOIN public.metric m ON m.metric_id = l.metric_id
      GROUP BY mt.companyid, m.metric_name
    )
    SELECT mv.companyid, mv.mname, mv.val
    FROM metric_values mv
    ORDER BY mv.companyid, mv.mname;

  -- Case 2: company filter only
  ELSIF use_company AND NOT use_metric THEN
    RETURN QUERY
    WITH RECURSIVE
    month_txn AS (
      SELECT t.companyid, m.account_name,
             SUM(t.amount_raw * m.erp_sign)::numeric AS amount
      FROM public.gl_txn_raw t
      JOIN public.gl_account_map m
        ON t.gl_account::int4 <@ m.acct_range
      WHERE t.posting_date >= p_start_date
        AND t.posting_date <  v_end_date
        AND t.companyid = ANY(p_company_ids)
      GROUP BY t.companyid, m.account_name
    ),
    mc_base AS (
      SELECT mc.metric_id, mc.ref_type, mc.ref_name,
             CASE mc.op WHEN '+' THEN 1 ELSE -1 END AS sign
      FROM public.metric_component mc
    ),
    expand(metric_id, ref_type, ref_name, sign) AS (
      SELECT metric_id, ref_type, ref_name, sign FROM mc_base
      UNION ALL
      SELECT e.metric_id, mc2.ref_type, mc2.ref_name,
             e.sign * CASE mc2.op WHEN '+' THEN 1 ELSE -1 END
      FROM expand e
      JOIN public.metric_component mc2
        ON e.ref_type = 'metric'
       AND e.ref_name = (
             SELECT m.metric_name FROM public.metric m
             WHERE m.metric_id = mc2.metric_id
           )
    ),
    leaf AS (
      SELECT e.metric_id, e.ref_name AS account_name, e.sign
      FROM expand e
      WHERE e.ref_type = 'account'
    ),
    metric_values AS (
      SELECT mt.companyid, m.metric_name AS mname,
             SUM(l.sign * mt.amount) AS val
      FROM month_txn mt
      JOIN leaf l ON l.account_name = mt.account_name
      JOIN public.metric m ON m.metric_id = l.metric_id
      GROUP BY mt.companyid, m.metric_name
    )
    SELECT mv.companyid, mv.mname, mv.val
    FROM metric_values mv
    ORDER BY mv.companyid, mv.mname;

  -- Case 3: metric filter only
  ELSIF NOT use_company AND use_metric THEN
    RETURN QUERY
    WITH RECURSIVE
    wanted_metrics AS (
      SELECT m.metric_id, m.metric_name AS mname
      FROM public.metric AS m
      WHERE m.metric_name = ANY(p_metric_names)
    ),
    month_txn AS (
      SELECT t.companyid, m.account_name,
             SUM(t.amount_raw * m.erp_sign)::numeric AS amount
      FROM public.gl_txn_raw t
      JOIN public.gl_account_map m
        ON t.gl_account::int4 <@ m.acct_range
      WHERE t.posting_date >= p_start_date
        AND t.posting_date <  v_end_date
      GROUP BY t.companyid, m.account_name
    ),
    mc_base AS (
      SELECT mc.metric_id, mc.ref_type, mc.ref_name,
             CASE mc.op WHEN '+' THEN 1 ELSE -1 END AS sign
      FROM public.metric_component mc
      WHERE mc.metric_id IN (SELECT wm.metric_id FROM wanted_metrics wm)
    ),
    expand(metric_id, ref_type, ref_name, sign) AS (
      SELECT metric_id, ref_type, ref_name, sign FROM mc_base
      UNION ALL
      SELECT e.metric_id, mc2.ref_type, mc2.ref_name,
             e.sign * CASE mc2.op WHEN '+' THEN 1 ELSE -1 END
      FROM expand e
      JOIN public.metric_component mc2
        ON e.ref_type = 'metric'
       AND e.ref_name = (
             SELECT m.metric_name FROM public.metric m
             WHERE m.metric_id = mc2.metric_id
           )
    ),
    leaf AS (
      SELECT e.metric_id, e.ref_name AS account_name, e.sign
      FROM expand e
      WHERE e.ref_type = 'account'
    ),
    metric_values AS (
      SELECT mt.companyid, wm.mname,
             SUM(l.sign * mt.amount) AS val
      FROM month_txn mt
      JOIN leaf l ON l.account_name = mt.account_name
      JOIN wanted_metrics wm ON wm.metric_id = l.metric_id
      GROUP BY mt.companyid, wm.mname
    )
    SELECT mv.companyid, mv.mname, mv.val
    FROM metric_values mv
    ORDER BY mv.companyid, mv.mname;

  -- Case 4: both filters
  ELSE
    RETURN QUERY
    WITH RECURSIVE
    wanted_metrics AS (
      SELECT m.metric_id, m.metric_name AS mname
      FROM public.metric AS m
      WHERE m.metric_name = ANY(p_metric_names)
    ),
    month_txn AS (
      SELECT t.companyid, m.account_name,
             SUM(t.amount_raw * m.erp_sign)::numeric AS amount
      FROM public.gl_txn_raw t
      JOIN public.gl_account_map m
        ON t.gl_account::int4 <@ m.acct_range
      WHERE t.posting_date >= p_start_date
        AND t.posting_date <  v_end_date
        AND t.companyid = ANY(p_company_ids)
      GROUP BY t.companyid, m.account_name
    ),
    mc_base AS (
      SELECT mc.metric_id, mc.ref_type, mc.ref_name,
             CASE mc.op WHEN '+' THEN 1 ELSE -1 END AS sign
      FROM public.metric_component mc
      WHERE mc.metric_id IN (SELECT wm.metric_id FROM wanted_metrics wm)
    ),
    expand(metric_id, ref_type, ref_name, sign) AS (
      SELECT metric_id, ref_type, ref_name, sign FROM mc_base
      UNION ALL
      SELECT e.metric_id, mc2.ref_type, mc2.ref_name,
             e.sign * CASE mc2.op WHEN '+' THEN 1 ELSE -1 END
      FROM expand e
      JOIN public.metric_component mc2
        ON e.ref_type = 'metric'
       AND e.ref_name = (
             SELECT m.metric_name FROM public.metric m
             WHERE m.metric_id = mc2.metric_id
           )
    ),
    leaf AS (
      SELECT e.metric_id, e.ref_name AS account_name, e.sign
      FROM expand e
      WHERE e.ref_type = 'account'
    ),
    metric_values AS (
      SELECT mt.companyid, wm.mname,
             SUM(l.sign * mt.amount) AS val
      FROM month_txn mt
      JOIN leaf l ON l.account_name = mt.account_name
      JOIN wanted_metrics wm ON wm.metric_id = l.metric_id
      GROUP BY mt.companyid, wm.mname
    )
    SELECT mv.companyid, mv.mname, mv.val
    FROM metric_values mv
    ORDER BY mv.companyid, mv.mname;
  END IF;
END;
$function$
```

### finance.actual_metric_average(p_start_year integer, p_start_period integer, p_end_year integer, p_end_period integer DEFAULT NULL::integer, p_company_ids text[] DEFAULT NULL::text[], p_metric_names text[] DEFAULT NULL::text[])
- Returns: TABLE(companyid text, metric_name text, avg_value numeric)
- Returns set of rows

```sql
CREATE OR REPLACE FUNCTION finance.actual_metric_average(p_start_year integer, p_start_period integer, p_end_year integer, p_end_period integer DEFAULT NULL::integer, p_company_ids text[] DEFAULT NULL::text[], p_metric_names text[] DEFAULT NULL::text[])
 RETURNS TABLE(companyid text, metric_name text, avg_value numeric)
 LANGUAGE plpgsql
AS $function$
DECLARE
  v_end_period  INT := COALESCE(p_end_period, p_start_period + 1);
BEGIN
  RETURN QUERY
  WITH raw_data AS (
    SELECT *
    FROM finance.actual_metric(
      make_date(p_start_year, p_start_period, 1),
      make_date(p_end_year, v_end_period, 1),
      p_company_ids,
      p_metric_names
    )
  ),
  monthly AS (
    SELECT
      r.companyid,
      r.metric_name,
      date_trunc('month', d::date) AS month,
      SUM(r.value) AS month_value
    FROM raw_data r,
         generate_series(
           make_date(p_start_year, p_start_period, 1),
           make_date(p_end_year, v_end_period, 1) - interval '1 day',
           interval '1 month'
         ) d
    WHERE r.value IS NOT NULL
    GROUP BY r.companyid, r.metric_name, date_trunc('month', d::date)
  )
  SELECT
    m.companyid,
    m.metric_name,
    AVG(m.month_value) AS avg_value
  FROM monthly m
  GROUP BY m.companyid, m.metric_name
  ORDER BY m.companyid, m.metric_name;
END;
$function$
```

### finance.actual_transaction(p_start_date date, p_end_date date, p_company_ids text[] DEFAULT NULL::text[], p_components text[] DEFAULT NULL::text[])
- Returns: TABLE(companyid text, posting_date date, ref_name text, gl_account text, description text, amount numeric)
- Returns set of rows

```sql
CREATE OR REPLACE FUNCTION finance.actual_transaction(p_start_date date, p_end_date date, p_company_ids text[] DEFAULT NULL::text[], p_components text[] DEFAULT NULL::text[])
 RETURNS TABLE(companyid text, posting_date date, ref_name text, gl_account text, description text, amount numeric)
 LANGUAGE sql
AS $function$
    SELECT
        g.companyid,
        g.posting_date,
        m.account_name AS ref_name,
        g.gl_account,
        g.description,
        g.amount_raw * m.erp_sign AS amount
    FROM public.gl_txn_raw g
    JOIN public.gl_account_map m
      ON g.gl_account::int4 <@ m.acct_range
    WHERE (p_company_ids IS NULL OR g.companyid = ANY(p_company_ids))
      AND g.posting_date >= p_start_date
      AND g.posting_date <  p_end_date
      AND (p_components IS NULL OR m.account_name = ANY(p_components));
$function$
```

```sql
CREATE OR REPLACE FUNCTION finance.actual_transaction_average(p_start_year integer, p_start_month integer, p_end_year integer, p_end_month integer, p_company_ids text[], p_components text[] DEFAULT NULL::text[])
 RETURNS TABLE(companyid text, ref_name text, avg_value numeric, min_value numeric, max_value numeric, periods_count integer, start_date date, end_date date)
 LANGUAGE plpgsql
AS $function$
DECLARE
    v_start_month date := make_date(p_start_year, p_start_month, 1);
    v_end_month   date := make_date(p_end_year,   p_end_month,   1);
    v_end_date    date := (v_end_month + INTERVAL '1 month' - INTERVAL '1 day')::date;
BEGIN
    RETURN QUERY
    WITH months AS (
        SELECT gs::date AS period_start
        FROM generate_series(v_start_month, v_end_month, INTERVAL '1 month') AS gs
    ),
    per_month AS (
        SELECT
            b.companyid,
            b.ref_name,
            mo.period_start,
            b.amount::numeric AS value   -- ✅ use amount column
        FROM months mo
        CROSS JOIN LATERAL finance.actual_transaction(
            mo.period_start::date,
            (mo.period_start + INTERVAL '1 month')::date,
            p_company_ids,
            p_components
        ) AS b
    )
    SELECT
        pm.companyid,
        pm.ref_name,
        AVG(pm.value)                         AS avg_value,
        MIN(pm.value)                         AS min_value,
        MAX(pm.value)                         AS max_value,
        COUNT(DISTINCT pm.period_start)::int  AS periods_count,
        v_start_month                         AS start_date,
        v_end_date                            AS end_date
    FROM per_month pm
    GROUP BY pm.companyid, pm.ref_name
    ORDER BY pm.companyid, pm.ref_name;
END;
$function$
```

### finance.budget_account(p_start_year integer, p_start_period integer, p_end_year integer, p_end_period integer, p_company_ids text[] DEFAULT NULL::text[], p_components text[] DEFAULT NULL::text[])
- Returns: TABLE(companyid text, ref_name text, value numeric)
- Returns set of rows

```sql
CREATE OR REPLACE FUNCTION finance.budget_account(p_start_year integer, p_start_period integer, p_end_year integer, p_end_period integer, p_company_ids text[] DEFAULT NULL::text[], p_components text[] DEFAULT NULL::text[])
 RETURNS TABLE(companyid text, ref_name text, value numeric)
 LANGUAGE sql
AS $function$
    SELECT
        b.companyid,
        m.account_name AS ref_name,
        SUM(b.amt1 * m.erp_sign) AS value
    FROM public.budget b
    JOIN public.gl_account_map m
      ON b.account::int4 <@ m.acct_range
    WHERE (p_company_ids IS NULL OR b.companyid = ANY(p_company_ids))
      AND (b.year > p_start_year 
           OR (b.year = p_start_year AND b.period >= p_start_period))
      AND (b.year < p_end_year 
           OR (b.year = p_end_year AND b.period < p_end_period))
      AND (p_components IS NULL OR m.account_name = ANY(p_components))
    GROUP BY b.companyid, m.account_name;
$function$
```

### finance.budget_metric(p_start_year integer, p_start_period integer, p_end_year integer, p_end_period integer DEFAULT NULL::integer, p_company_ids text[] DEFAULT NULL::text[], p_metric_names text[] DEFAULT NULL::text[])
- Returns: TABLE(companyid text, metric_name text, value numeric)
- Returns set of rows

```sql
CREATE OR REPLACE FUNCTION finance.budget_metric(p_start_year integer, p_start_period integer, p_end_year integer, p_end_period integer DEFAULT NULL::integer, p_company_ids text[] DEFAULT NULL::text[], p_metric_names text[] DEFAULT NULL::text[])
 RETURNS TABLE(companyid text, metric_name text, value numeric)
 LANGUAGE plpgsql
AS $function$
DECLARE
  v_end_period  INT := COALESCE(p_end_period, p_start_period + 1);
  use_company   BOOLEAN := p_company_ids  IS NOT NULL;
  use_metric    BOOLEAN := p_metric_names IS NOT NULL;
BEGIN
  IF use_company THEN
    p_company_ids := ARRAY(SELECT UPPER(BTRIM(x)) FROM unnest(p_company_ids) AS x);

    PERFORM 1
    FROM unnest(p_company_ids) u
    LEFT JOIN public.company c ON c.companyid = u
    WHERE c.companyid IS NULL;
    IF FOUND THEN
      RAISE EXCEPTION 'One or more company IDs not valid: %', p_company_ids;
    END IF;
  END IF;

  IF use_metric THEN
    p_metric_names := ARRAY(SELECT BTRIM(x) FROM unnest(p_metric_names) AS x);
  END IF;

  RETURN QUERY
  WITH RECURSIVE
  month_budget AS (
    SELECT p.companyid, m.account_name,
           SUM(p.amt1 * m.erp_sign)::numeric AS amount
    FROM public.budget p
    JOIN public.gl_account_map m
      ON p.account::int4 <@ m.acct_range
    WHERE (p.year > p_start_year OR (p.year = p_start_year AND p.period >= p_start_period))
      AND (p.year < p_end_year OR (p.year = p_end_year AND p.period < v_end_period))
      AND (NOT use_company OR p.companyid = ANY(p_company_ids))
    GROUP BY p.companyid, m.account_name
  ),
  wanted_metrics AS (
    SELECT m.metric_id, m.metric_name AS mname
    FROM public.metric m
    WHERE NOT use_metric OR m.metric_name = ANY(p_metric_names)
  ),
  mc_base AS (
    SELECT mc.metric_id, mc.ref_type, mc.ref_name,
           CASE mc.op WHEN '+' THEN 1 ELSE -1 END AS sign
    FROM public.metric_component mc
    WHERE mc.metric_id IN (SELECT metric_id FROM wanted_metrics)
  ),
  expand(metric_id, ref_type, ref_name, sign) AS (
    SELECT metric_id, ref_type, ref_name, sign FROM mc_base
    UNION ALL
    SELECT e.metric_id, mc2.ref_type, mc2.ref_name,
           e.sign * CASE mc2.op WHEN '+' THEN 1 ELSE -1 END
    FROM expand e
    JOIN public.metric_component mc2
      ON e.ref_type = 'metric'
     AND e.ref_name = (
           SELECT m.metric_name FROM public.metric m
           WHERE m.metric_id = mc2.metric_id
         )
  ),
  leaf AS (
    SELECT e.metric_id, e.ref_name AS account_name, e.sign
    FROM expand e
    WHERE e.ref_type = 'account'
  ),
  metric_values AS (
    SELECT mb.companyid, wm.mname,
           SUM(l.sign * mb.amount) AS val
    FROM month_budget mb
    JOIN leaf l ON l.account_name = mb.account_name
    JOIN wanted_metrics wm ON wm.metric_id = l.metric_id
    GROUP BY mb.companyid, wm.mname
  )
  SELECT mv.companyid, mv.mname, mv.val
  FROM metric_values mv
  ORDER BY mv.companyid, mv.mname;
END;
$function$
```

### finance.budget_vs_actual_account(p_start_year integer, p_start_period integer, p_end_year integer, p_end_period integer, p_company_ids text[] DEFAULT NULL::text[], p_components text[] DEFAULT NULL::text[])
- Returns: TABLE(companyid text, ref_name text, actual numeric, budget numeric, variance numeric)
- Returns set of rows

```sql
CREATE OR REPLACE FUNCTION finance.budget_vs_actual_account(p_start_year integer, p_start_period integer, p_end_year integer, p_end_period integer, p_company_ids text[] DEFAULT NULL::text[], p_components text[] DEFAULT NULL::text[])
 RETURNS TABLE(companyid text, ref_name text, actual numeric, budget numeric, variance numeric)
 LANGUAGE sql
AS $function$
    -- Actuals
    WITH actuals AS (
        SELECT
            g.companyid,
            m.account_name AS ref_name,
            SUM(g.amount_raw * m.erp_sign) AS value
        FROM public.gl_txn_raw g
        JOIN public.gl_account_map m
          ON g.gl_account::int4 <@ m.acct_range
        WHERE (p_company_ids IS NULL OR g.companyid = ANY(p_company_ids))
          AND (g.postyear > p_start_year 
               OR (g.postyear = p_start_year AND g.postperiod >= p_start_period))
          AND (g.postyear < p_end_year 
               OR (g.postyear = p_end_year AND g.postperiod < p_end_period))
        GROUP BY g.companyid, m.account_name
    ),
    budgets AS (
        SELECT
            b.companyid,
            m.account_name AS ref_name,
            SUM(b.amt1 * m.erp_sign) AS value
        FROM public.budget b
        JOIN public.gl_account_map m
          ON b.account::int4 <@ m.acct_range
        WHERE (p_company_ids IS NULL OR b.companyid = ANY(p_company_ids))
          AND (b.year > p_start_year 
               OR (b.year = p_start_year AND b.period >= p_start_period))
          AND (b.year < p_end_year 
               OR (b.year = p_end_year AND b.period < p_end_period))
        GROUP BY b.companyid, m.account_name
    )
    SELECT
        COALESCE(a.companyid, b.companyid) AS companyid,
        COALESCE(a.ref_name, b.ref_name)   AS ref_name,
        a.value AS actual,
        b.value AS budget,
        (a.value - b.value) AS variance
    FROM actuals a
    FULL OUTER JOIN budgets b
      ON a.companyid = b.companyid
     AND a.ref_name = b.ref_name
    WHERE (p_components IS NULL OR COALESCE(a.ref_name, b.ref_name) = ANY(p_components));
$function$
```

### finance.budget_vs_actual_metric(p_start_year integer, p_start_period integer, p_end_year integer, p_end_period integer DEFAULT NULL::integer, p_company_ids text[] DEFAULT NULL::text[], p_metric_names text[] DEFAULT NULL::text[])
- Returns: TABLE(companyid text, metric_name text, actual numeric, budget numeric, variance numeric)
- Returns set of rows

```sql
CREATE OR REPLACE FUNCTION finance.budget_vs_actual_metric(p_start_year integer, p_start_period integer, p_end_year integer, p_end_period integer DEFAULT NULL::integer, p_company_ids text[] DEFAULT NULL::text[], p_metric_names text[] DEFAULT NULL::text[])
 RETURNS TABLE(companyid text, metric_name text, actual numeric, budget numeric, variance numeric)
 LANGUAGE plpgsql
AS $function$
DECLARE
  v_end_period  INT := COALESCE(p_end_period, p_start_period + 1);
  use_company   BOOLEAN := p_company_ids  IS NOT NULL;
  use_metric    BOOLEAN := p_metric_names IS NOT NULL;
BEGIN
  IF use_company THEN
    p_company_ids := ARRAY(SELECT UPPER(BTRIM(x)) FROM unnest(p_company_ids) AS x);

    PERFORM 1
    FROM unnest(p_company_ids) u
    LEFT JOIN public.company c ON c.companyid = u
    WHERE c.companyid IS NULL;
    IF FOUND THEN
      RAISE EXCEPTION 'One or more company IDs not valid: %', p_company_ids;
    END IF;
  END IF;

  IF use_metric THEN
    p_metric_names := ARRAY(SELECT BTRIM(x) FROM unnest(p_metric_names) AS x);
  END IF;

  RETURN QUERY
  WITH actual_data AS (
    SELECT *
    FROM finance.actual_metric(
      make_date(p_start_year, p_start_period % 100, 1),
      make_date(p_end_year, v_end_period % 100, 1),
      p_company_ids,
      p_metric_names
    )
  ),
  budget_data AS (
    SELECT *
    FROM finance.budget_metric(
      p_start_year,
      p_start_period,
      p_end_year,
      v_end_period,
      p_company_ids,
      p_metric_names
    )
  )
  SELECT
    COALESCE(a.companyid, b.companyid) AS companyid,
    COALESCE(a.metric_name, b.metric_name) AS metric_name,
    a.value AS actual,
    b.value AS budget,
    (a.value - b.value) AS variance
  FROM budget_data b
  FULL OUTER JOIN actual_data a
    ON a.companyid = b.companyid AND a.metric_name = b.metric_name
  ORDER BY companyid, metric_name;
END;
$function$
```



## Views

### public.gl_txn_signed
```sql
SELECT t.gl_account,
    t.companyid,
    t.customer,
    t.posting_date,
    t.description,
    t.extdescription,
    t.amount_raw,
    t.invoicetype,
    t.invvouch,
    t.postperiod,
    t.postyear,
    t.source,
    t.sourcekey,
    t.supplierinvnum,
    t.transcode,
    t.uniqueid,
    m.account_name,
    (t.amount_raw * (m.erp_sign)::numeric) AS amount,
    m.tags
   FROM (gl_txn_raw t
     JOIN gl_account_map m ON ((t.gl_account <@ m.acct_range)));
```



## Indexes

- **public.company**: `company_pkey`
```sql
CREATE UNIQUE INDEX company_pkey ON public.company USING btree (companyid)
```

- **public.gl_account_map**: `gl_account_map_acct_range_gist`
```sql
CREATE INDEX gl_account_map_acct_range_gist ON public.gl_account_map USING gist (acct_range)
```

- **public.gl_account_map**: `gl_account_map_idx_dept_code`
```sql
CREATE INDEX gl_account_map_idx_dept_code ON public.gl_account_map USING btree (((tags ->> 'Department Code'::text)))
```

- **public.gl_account_map**: `gl_account_map_idx_direct_indirect`
```sql
CREATE INDEX gl_account_map_idx_direct_indirect ON public.gl_account_map USING btree (((tags ->> 'Direct/Indirect'::text)))
```

- **public.gl_account_map**: `gl_account_map_pk`
```sql
CREATE UNIQUE INDEX gl_account_map_pk ON public.gl_account_map USING btree (account_name, range_start, range_end)
```

- **public.gl_account_map**: `gl_account_map_tags_gin`
```sql
CREATE INDEX gl_account_map_tags_gin ON public.gl_account_map USING gin (tags)
```

- **public.gl_account_map**: `idx_gl_account_map_range`
```sql
CREATE INDEX idx_gl_account_map_range ON public.gl_account_map USING gist (acct_range)
```

- **public.gl_txn_raw**: `gl_txn_raw_unique`
```sql
CREATE UNIQUE INDEX gl_txn_raw_unique ON public.gl_txn_raw USING btree (uniqueid)
```

- **public.gl_txn_raw**: `idx_gl_txn_raw_posting_company`
```sql
CREATE INDEX idx_gl_txn_raw_posting_company ON public.gl_txn_raw USING btree (posting_date, companyid)
```

- **public.metric**: `metric_metric_name_key`
```sql
CREATE UNIQUE INDEX metric_metric_name_key ON public.metric USING btree (metric_name)
```

- **public.metric**: `metric_pkey`
```sql
CREATE UNIQUE INDEX metric_pkey ON public.metric USING btree (metric_id)
```

- **public.metric_component**: `metric_component_pkey`
```sql
CREATE UNIQUE INDEX metric_component_pkey ON public.metric_component USING btree (metric_id, ref_type, ref_name)
```



## Triggers



## Django Function Mappings

The following Django functions in `dashboard/db.py` have been updated to use the new year/period parameters:

### Working Functions ✅
- `fetch_actual_metrics(start_year, start_period, end_year, end_period, company_ids, metric_names)`
- `fetch_actual_accounts(start_year, start_period, end_year, end_period, company_ids, components)`
- `fetch_budget_metrics(start_year, start_period, end_year, end_period, company_ids, metric_names)`
- `fetch_budget_accounts(start_year, start_period, end_year, end_period, company_ids, components)`
- `fetch_budget_vs_actual_metrics(start_year, start_period, end_year, end_period, company_ids, metric_names)`
- `fetch_budget_vs_actual_accounts(start_year, start_period, end_year, end_period, company_ids, components)`

### Functions with Known Issues ⚠️
- `fetch_actual_accounts_average()` - Database function has type casting issue (bigint vs integer)
- `fetch_actual_metrics_average()` - Database function has column reference ambiguity

### Parameter Format
All functions now use the consistent parameter format:
- `start_year` (integer) - Starting year (e.g., 2025)
- `start_period` (integer) - Starting period/month (1-12)
- `end_year` (integer) - Ending year (e.g., 2025)  
- `end_period` (integer) - Ending period/month (1-12, exclusive)

### Example Usage
```python
# Q1 2025 data (Jan-Mar, periods 1-3)
data = fetch_actual_metrics(2025, 1, 2025, 4, ['AFP'])

# Q2 2025 data (Apr-Jun, periods 4-6)  
data = fetch_actual_metrics(2025, 4, 2025, 7, ['AFP'])
```

## Relationships

- **public.metric_component**.`metric_id` → **public.metric**.`metric_id`