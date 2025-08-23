# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Django web application called `fpna_django_app` that provides financial dashboard functionality for budget vs. actual reporting. The application uses PostgreSQL (Neon database) and consists of a single Django app called `fpna_app`.

## Architecture

- **Main Django Project**: `project/` - Contains settings, main URLs, and WSGI configuration
- **FP&A App**: `fpna_app/` - Contains the core business logic with views, URLs, database functions, and templates
- **Database Layer**: Direct SQL queries using stored functions (`actual_metric()`, `actual_account()`) via Django's cursor interface in `fpna_app/db.py`
- **Frontend**: HTMX-powered interface with Tailwind CSS styling and Alpine.js for interactivity

## Key Components

### Database Integration
- PostgreSQL database hosted on Neon (connection details in `project/settings.py`)
- Uses the `finance` schema with comprehensive stored functions for financial calculations
- Raw SQL queries executed through `fpna_app/db.py` functions:
  - `fetch_actual_metrics(start_date, end_date)` - Calls `finance.actual_metric()` stored function
  - `fetch_actual_accounts(start_date, end_date)` - Calls `finance.actual_account()` stored function

#### Key Database Components
- **Tables**: `budget`, `company`, `gl_account_map`, `gl_txn_raw`, `gl_txn_signed`, `metric`, `metric_component`
- **Core Functions Available**:
  - `finance.actual_account()` - Account-level actual values
  - `finance.actual_metric()` - Metric-level actual values with recursive component calculation
  - `finance.budget_account()` - Budget data by account
  - `finance.budget_metric()` - Budget data by metric
  - `finance.budget_vs_actual_account()` - Variance analysis at account level
  - `finance.budget_vs_actual_metric()` - Variance analysis at metric level
  - Functions also support averaging (`actual_account_average`, `actual_metric_average`)
- **Key Features**: Account mapping via `gl_account_map.acct_range`, metric calculations via recursive component expansion

### URL Structure
- Root URL (`/`) serves the budget vs. actual dashboard
- `/load-metrics/` - HTMX endpoint for loading metrics data
- `/load-accounts/` - HTMX endpoint for loading accounts data  
- `/dashboard/` - Alternative dashboard view
- `/admin/` - Django admin interface

### Frontend Stack
- HTMX for dynamic content loading without full page refreshes
- Alpine.js for client-side interactivity
- Tailwind CSS for styling (served from `fpna_app/static/css/tailwind.css`)

## Development Commands

Standard Django development commands:

```bash
# Run development server
python manage.py runserver

# Database migrations (if needed)
python manage.py makemigrations
python manage.py migrate

# Create superuser for admin access
python manage.py createsuperuser

# Django shell for testing
python manage.py shell
```

## Important Notes

- Database credentials are currently hardcoded in settings.py (should be moved to environment variables for production)
- The application relies on PostgreSQL stored functions that must exist in the database
- Templates are located in `fpna_app/templates/` directory
- Static files (CSS) are in `fpna_app/static/` directory
- No requirements.txt file present - Django and psycopg2 are minimum dependencies

## Available Documentation

- `docs/database.md` - Complete database schema documentation with all tables, functions, and relationships
- `docs/database_function_examples.py` - Python test examples showing how to call the finance functions
- `docs/style.png` - UI reference image

## Testing Database Functions

The `docs/database_function_examples.py` file contains example calls to all finance functions for testing purposes. These examples show proper parameter usage and expected data formats.