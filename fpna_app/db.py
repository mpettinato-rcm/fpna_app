from django.db import connection

def fetch_actual_metrics(start_year, start_period, end_year, end_period, company_ids=None, metric_names=None):
    """
    Fetch actual metrics data using the finance.actual_metric function
    """
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM finance.actual_metric(%s, %s, %s, %s, %s, %s)", 
                      [start_year, start_period, end_year, end_period, company_ids, metric_names])
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

def fetch_actual_accounts(start_year, start_period, end_year, end_period, company_ids=None, components=None):
    """
    Fetch actual account data using the finance.actual_account function
    """
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM finance.actual_account(%s, %s, %s, %s, %s, %s)", 
                      [start_year, start_period, end_year, end_period, company_ids, components])
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

def fetch_budget_accounts(start_year, start_period, end_year, end_period, company_ids=None, components=None):
    """
    Fetch budget account data using the finance.budget_account function
    """
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM finance.budget_account(%s, %s, %s, %s, %s, %s)", 
                      [start_year, start_period, end_year, end_period, company_ids, components])
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

def fetch_budget_metrics(start_year, start_period, end_year, end_period, company_ids=None, metric_names=None):
    """
    Fetch budget metrics data using the finance.budget_metric function
    """
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM finance.budget_metric(%s, %s, %s, %s, %s, %s)", 
                      [start_year, start_period, end_year, end_period, company_ids, metric_names])
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

def fetch_budget_vs_actual_accounts(start_year, start_period, end_year, end_period, company_ids=None, components=None):
    """
    Fetch budget vs actual account data using the finance.budget_vs_actual_account function
    """
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM finance.budget_vs_actual_account(%s, %s, %s, %s, %s, %s)", 
                      [start_year, start_period, end_year, end_period, company_ids, components])
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

def fetch_budget_vs_actual_metrics(start_year, start_period, end_year, end_period, company_ids=None, metric_names=None):
    """
    Fetch budget vs actual metrics data using the finance.budget_vs_actual_metric function
    """
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM finance.budget_vs_actual_metric(%s, %s, %s, %s, %s, %s)", 
                      [start_year, start_period, end_year, end_period, company_ids, metric_names])
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

def fetch_actual_accounts_average(start_year, start_period, end_year, end_period, company_ids=None, components=None):
    """
    Fetch actual account average data using the finance.actual_account_average function
    """
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM finance.actual_account_average(%s, %s, %s, %s, %s, %s)", 
                      [start_year, start_period, end_year, end_period, company_ids, components])
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

def fetch_actual_metrics_average(start_year, start_period, end_year, end_period, company_ids=None, metric_names=None):
    """
    Fetch actual metrics average data using the finance.actual_metric_average function
    """
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM finance.actual_metric_average(%s, %s, %s, %s, %s, %s)", 
                      [start_year, start_period, end_year, end_period, company_ids, metric_names])
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

def fetch_companies():
    """
    Fetch all companies from the public.company table
    """
    with connection.cursor() as cursor:
        cursor.execute("SELECT companyid FROM public.company ORDER BY companyid")
        return [row[0] for row in cursor.fetchall()]
