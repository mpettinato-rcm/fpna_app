from django.shortcuts import render, redirect
from .db import fetch_actual_metrics, fetch_actual_accounts, fetch_budget_metrics, fetch_budget_accounts, fetch_budget_vs_actual_accounts, fetch_budget_vs_actual_metrics, fetch_actual_accounts_average, fetch_actual_metrics_average

def budget_vs_actual_safe(request):
    # Simple version without database calls
    financial_data = [
        {"name": "Test Metric", "type": "metric", "q1_actual": 1000, "q2_actual": 1500, "q2_budget": 1200, "q2_average": 1100, "q3_budget": 1300, "variance": 300},
        {"name": "Test Account", "type": "account", "q1_actual": 500, "q2_actual": 600, "q2_budget": 550, "q2_average": 525, "q3_budget": 575, "variance": 50},
    ]
    
    context = {
        "financial_data": financial_data,
    }
    
    return render(request, "dashboard/budget_actual.html", context)

def budget_vs_actual(request):
    # Define the quarters using year/period format
    # Q1 2025 = periods 1-3 (Jan-Mar), Q2 2025 = periods 4-6 (Apr-Jun)
    
    # Get selected company from session, default to AFP
    try:
        selected_company = request.session.get('selected_company', 'AFP')
    except AttributeError:
        selected_company = 'AFP'  # Fallback if session not available
    company_ids = [selected_company]
    
    # Fetch Q1 2025 data (periods 1-3: Jan, Feb, Mar)
    # Using start_period=1, end_period=4 (half-open, so this gets periods 1, 2, 3)
    q1_accounts_data = fetch_actual_accounts(2025, 1, 2025, 4, company_ids)
    q1_metrics_data = fetch_actual_metrics(2025, 1, 2025, 4, company_ids)
    
    # Fetch Q2 2025 data (periods 4-6: Apr, May, Jun)
    # Using start_period=4, end_period=7 (half-open, so this gets periods 4, 5, 6)
    q2_accounts_data = fetch_actual_accounts(2025, 4, 2025, 7, company_ids)
    q2_metrics_data = fetch_actual_metrics(2025, 4, 2025, 7, company_ids)
    
    # Fetch Q2 2025 budget data (periods 4-6 for Q2: Apr, May, Jun)
    # Q2 = periods 4, 5, 6, so we use start_period=4, end_period=7 (half-open)
    q2_budget_accounts_data = fetch_budget_accounts(2025, 4, 2025, 7, company_ids)
    q2_budget_metrics_data = fetch_budget_metrics(2025, 4, 2025, 7, company_ids)
    
    # Fetch Q2 2025 budget vs actual variance data
    q2_variance_accounts_data = fetch_budget_vs_actual_accounts(2025, 4, 2025, 7, company_ids)
    q2_variance_metrics_data = fetch_budget_vs_actual_metrics(2025, 4, 2025, 7, company_ids)
    
    # Fetch Q2 2025 average data (same year/period parameters as budget)
    q2_average_accounts_data = fetch_actual_accounts_average(2025, 4, 2025, 7, company_ids)
    q2_average_metrics_data = fetch_actual_metrics_average(2025, 4, 2025, 7, company_ids)
    
    # Fetch Q3 2025 budget data (periods 7-9 for Q3: Jul, Aug, Sep)
    # Q3 = periods 7, 8, 9, so we use start_period=7, end_period=10 (half-open)
    q3_budget_accounts_data = fetch_budget_accounts(2025, 7, 2025, 10, company_ids)
    q3_budget_metrics_data = fetch_budget_metrics(2025, 7, 2025, 10, company_ids)
    
    # Convert to dictionaries for easier lookup
    q1_accounts_dict = {row['ref_name']: row for row in q1_accounts_data} if q1_accounts_data else {}
    q1_metrics_dict = {row['metric_name']: row for row in q1_metrics_data} if q1_metrics_data else {}
    
    q2_accounts_dict = {row['ref_name']: row for row in q2_accounts_data} if q2_accounts_data else {}
    q2_metrics_dict = {row['metric_name']: row for row in q2_metrics_data} if q2_metrics_data else {}
    
    q2_budget_accounts_dict = {row['ref_name']: row for row in q2_budget_accounts_data} if q2_budget_accounts_data else {}
    q2_budget_metrics_dict = {row['metric_name']: row for row in q2_budget_metrics_data} if q2_budget_metrics_data else {}
    
    q2_variance_accounts_dict = {row['ref_name']: row for row in q2_variance_accounts_data} if q2_variance_accounts_data else {}
    q2_variance_metrics_dict = {row['metric_name']: row for row in q2_variance_metrics_data} if q2_variance_metrics_data else {}
    
    q2_average_accounts_dict = {row['ref_name']: row for row in q2_average_accounts_data} if q2_average_accounts_data else {}
    q2_average_metrics_dict = {row['metric_name']: row for row in q2_average_metrics_data} if q2_average_metrics_data else {}
    
    q3_budget_accounts_dict = {row['ref_name']: row for row in q3_budget_accounts_data} if q3_budget_accounts_data else {}
    q3_budget_metrics_dict = {row['metric_name']: row for row in q3_budget_metrics_data} if q3_budget_metrics_data else {}
    
    # Define the exact order from your Excel list - COMPLETE VERSION with groups
    line_items = [
        # Sales Accounts group
        {"name": "Sales - Aluminum", "type": "account", "group": "gross_sales"},
        {"name": "Sales - DC VA", "type": "account", "group": "gross_sales"}, 
        {"name": "Sales - CNC VA", "type": "account", "group": "gross_sales"},
        {"name": "Sales - SEC VA", "type": "account", "group": "gross_sales"},
        {"name": "Sales - Intercompany", "type": "account", "group": "gross_sales"},
        {"name": "Sales - Outside Purchases", "type": "account", "group": "gross_sales"},
        {"name": "Gross Sales", "type": "metric", "group": "gross_sales", "is_group_header": True},
        
        # Sales Deduction Accounts group
        {"name": "Sales - Returns", "type": "account", "group": "sales_deductions"},
        {"name": "Sales - Discounts", "type": "account", "group": "sales_deductions"},
        {"name": "Sales - Allowances", "type": "account", "group": "sales_deductions"},
        {"name": "Sales Deductions", "type": "metric", "group": "sales_deductions", "is_group_header": True},
        {"name": "% of Sales", "type": "percentage"},
        
        {"name": "Net Sales", "type": "metric"},
        
        # Material Accounts group
        {"name": "Material - 304", "type": "account", "group": "total_metal_costs"},
        {"name": "Material - 360", "type": "account", "group": "total_metal_costs"},
        {"name": "Material - 365", "type": "account", "group": "total_metal_costs"},
        {"name": "Material - 369", "type": "account", "group": "total_metal_costs"},
        {"name": "Material - 380", "type": "account", "group": "total_metal_costs"},
        {"name": "Material - 383", "type": "account", "group": "total_metal_costs"},
        {"name": "Material - 384", "type": "account", "group": "total_metal_costs"},
        {"name": "Material - 390", "type": "account", "group": "total_metal_costs"},
        {"name": "Material - 413", "type": "account", "group": "total_metal_costs"},
        {"name": "Material - Twitch", "type": "account", "group": "total_metal_costs"},
        {"name": "Material - Discounts", "type": "account", "group": "total_metal_costs"},
        {"name": "Material - Scrap", "type": "account", "group": "total_metal_costs"},
        {"name": "Material - Inventory Change", "type": "account", "group": "total_metal_costs"},
        {"name": "Total Metal Costs", "type": "metric", "group": "total_metal_costs", "is_group_header": True},
        
        # CoS Accounts group
        {"name": "CoS - Impregnation", "type": "account", "group": "total_outside_costs"},
        {"name": "CoS - Inserts/Castings", "type": "account", "group": "total_outside_costs"},
        {"name": "CoS - Machining", "type": "account", "group": "total_outside_costs"},
        {"name": "CoS - Painting/Plating", "type": "account", "group": "total_outside_costs"},
        {"name": "CoS - Containers/Boxes", "type": "account", "group": "total_outside_costs"},
        {"name": "Total Outside Costs", "type": "metric", "group": "total_outside_costs", "is_group_header": True},
        
        {"name": "Total Material Costs", "type": "metric"},
        {"name": "% of Net Sales (x Tool)", "type": "percentage"},
        
        {"name": "Contribution (x Tool/CNC)", "type": "metric"},
        {"name": "Contribution (x Tool)", "type": "metric"},
        {"name": "% of Net Sales (x Tool)", "type": "percentage"},
        
        # Tooling Sales
        {"name": "Tooling Sales - New", "type": "account"},
        {"name": "Tooling Sales - Repairs", "type": "account"},
        {"name": "Tooling Sales - Perpetual", "type": "account"},
        {"name": "Tooling Sales", "type": "metric"},
        
        # Tooling Costs
        {"name": "Tooling Costs - New", "type": "account"},
        {"name": "Tooling Costs - Repairs", "type": "account"},
        {"name": "Tooling Costs - Perpetual", "type": "account"},
        {"name": "Tooling Costs", "type": "metric"},
        
        {"name": "Tooling Contribution", "type": "metric"},
        {"name": "% of Tooling Sales", "type": "percentage"},
        
        {"name": "Total Contribution", "type": "metric"},
        {"name": "% of Net Sales (x Tool)", "type": "percentage"},
        
        # Direct Labor group
        {"name": "Direct Labor", "type": "metric"},
        {"name": "Melt - Direct Labor", "type": "account", "group": "total_direct_labor"},
        {"name": "Melt - Direct Labor OT", "type": "account", "group": "total_direct_labor"},
        {"name": "DC - Direct Labor", "type": "account", "group": "total_direct_labor"},
        {"name": "DC - Direct Labor OT", "type": "account", "group": "total_direct_labor"},
        {"name": "FIN - Direct Labor", "type": "account", "group": "total_direct_labor"},
        {"name": "FIN - Direct Labor OT", "type": "account", "group": "total_direct_labor"},
        {"name": "CNC - Direct Labor", "type": "account", "group": "total_direct_labor"},
        {"name": "CNC - Direct Labor OT", "type": "account", "group": "total_direct_labor"},
        {"name": "Total Direct Labor", "type": "metric", "group": "total_direct_labor", "is_group_header": True},
        {"name": "% of Contribution x Tooling", "type": "percentage"},
        
        # Direct Expenses
        {"name": "Direct Expenses", "type": "metric"},
        {"name": "Melt - Flux", "type": "account"},
        {"name": "Melt - Supplies", "type": "account"},
        {"name": "DC - Hydraulic Fluid", "type": "account"},
        {"name": "DC - Die Lube", "type": "account"},
        {"name": "DC - Plunger Lube", "type": "account"},
        {"name": "DC - Hot Oil Expense", "type": "account"},
        {"name": "DC - Supplies", "type": "account"},
        {"name": "DC - Nitrogen/Gases", "type": "account"},
        {"name": "DC - Piston Tips", "type": "account"},
        {"name": "DC - Shot Sleeves", "type": "account"},
        {"name": "DC - Plunger Arms", "type": "account"},
        {"name": "DC - Impregnation", "type": "account"},
        {"name": "FIN - Supplies", "type": "account"},
        {"name": "CNC - Fluids", "type": "account"},
        {"name": "CNC - Perishable Tools", "type": "account"},
        {"name": "CNC - Machine Maintenance", "type": "account"},
        {"name": "CNC - Outside Maintenance", "type": "account"},
        {"name": "MAINT - Air Compressors", "type": "account"},
        {"name": "MAINT - Automated Equipment", "type": "account"},
        {"name": "MAINT - Cranes", "type": "account"},
        {"name": "MAINT - DC Machines", "type": "account"},
        {"name": "MAINT - Trim Presses", "type": "account"},
        {"name": "MAINT - Furnaces", "type": "account"},
        {"name": "MAINT - Fork Lift Trucks", "type": "account"},
        {"name": "MAINT - Shot Blast", "type": "account"},
        {"name": "MAINT - Evap/Cooling Tower", "type": "account"},
        {"name": "TR - Outside Shops", "type": "account"},
        {"name": "TR - Ejector/Core/Leader Pins", "type": "account"},
        {"name": "TR - Supplies", "type": "account"},
        {"name": "QA - Gages/Supplies", "type": "account"},
        {"name": "QA - Sorting", "type": "account"},
        {"name": "SHPG - Supplies", "type": "account"},
        {"name": "SHPG - Freight In", "type": "account"},
        {"name": "SHPG - Premium FRT Out", "type": "account"},
        {"name": "SHPG - Freight on Returns", "type": "account"},
        {"name": "GF - General Supplies", "type": "account"},
        {"name": "GF - Satefy Supplies", "type": "account"},
        {"name": "GF - Janitorial Supplies", "type": "account"},
        {"name": "GF - Uniforms", "type": "account"},
        {"name": "GF - Building Maintenance", "type": "account"},
        {"name": "GF - Waste Water Disposal", "type": "account"},
        {"name": "Total Direct Expenses", "type": "metric"},
        {"name": "% of Contribution x Tooling", "type": "percentage"},
        
        {"name": "Total Direct", "type": "metric"},
        {"name": "% of Contribution x Tooling", "type": "percentage"},
        
        # Indirect Labor
        {"name": "Indirect Labor", "type": "metric"},
        {"name": "Melt - Indirect Labor", "type": "account"},
        {"name": "Melt - Indirect Labor OT", "type": "account"},
        {"name": "DC - Indirect Labor", "type": "account"},
        {"name": "DC - Indirect Labor OT", "type": "account"},
        {"name": "FIN - Indirect Labor", "type": "account"},
        {"name": "FIN - Indirect Labor OT", "type": "account"},
        {"name": "CNC - Indirect Labor", "type": "account"},
        {"name": "CNC - Indirect Labor OT", "type": "account"},
        {"name": "PCS - Indirect Labor", "type": "account"},
        {"name": "PCS - Indirect Labor OT", "type": "account"},
        {"name": "MAINT - Indirect Labor", "type": "account"},
        {"name": "MAINT - Indirect Labor OT", "type": "account"},
        {"name": "TR - Indirect Labor", "type": "account"},
        {"name": "TR - Indirect Labor OT", "type": "account"},
        {"name": "QA - Indirect Labor", "type": "account"},
        {"name": "QA - Indirect Labor OT", "type": "account"},
        {"name": "SHPG - Indirect Labor", "type": "account"},
        {"name": "SHPG - Indirect Labor OT", "type": "account"},
        {"name": "ENG - Indirect Labor", "type": "account"},
        {"name": "ENG - Indirect Labor OT", "type": "account"},
        {"name": "GF - Indirect Labor", "type": "account"},
        {"name": "SGA - Indirect Labor", "type": "account"},
        {"name": "SGA - Indirect Labor OT", "type": "account"},
        {"name": "Total Indirect Labor", "type": "metric"},
        {"name": "% of Contribution x Tooling", "type": "percentage"},
        
        # Indirect Expenses
        {"name": "Indirect Expenses", "type": "metric"},
        {"name": "QA - IATF Fees", "type": "account"},
        {"name": "GF - Training/Education", "type": "account"},
        {"name": "GF - Depreciation", "type": "account"},
        {"name": "GF - Electricity", "type": "account"},
        {"name": "GF - Water", "type": "account"},
        {"name": "GF - Natural Gas", "type": "account"},
        {"name": "GF - Propane", "type": "account"},
        {"name": "GF - General Liability Ins.", "type": "account"},
        {"name": "GF - Property Taxes", "type": "account"},
        {"name": "GF - Meridian Leases", "type": "account"},
        {"name": "GF - Equipment Lease/Rental", "type": "account"},
        {"name": "GF - Building Expense", "type": "account"},
        {"name": "SGA - Commissions", "type": "account"},
        {"name": "SGA - Supplies/Fees", "type": "account"},
        {"name": "SGA - Professional Services", "type": "account"},
        {"name": "SGA - Phone/Data", "type": "account"},
        {"name": "SGA - Travel/Entertainment", "type": "account"},
        {"name": "SGA - Vehicle Expense", "type": "account"},
        {"name": "SGA - Recruiting/Relocation", "type": "account"},
        {"name": "SGA - Corporate Expenses", "type": "account"},
        {"name": "SGA - Payroll Fees", "type": "account"},
        {"name": "SGA - Outside Janitorial", "type": "account"},
        {"name": "GF - Management Bonus", "type": "account"},
        {"name": "GF - Vacation/Holiday Pay", "type": "account"},
        {"name": "GF - 401k Match", "type": "account"},
        {"name": "GF - Payroll Taxes", "type": "account"},
        {"name": "GF - Workers Comp", "type": "account"},
        {"name": "GF - Life Insurance", "type": "account"},
        {"name": "GF - Health Insurance", "type": "account"},
        {"name": "GF - Profit Sharing", "type": "account"},
        {"name": "Total Indirect Expenses", "type": "metric"},
        {"name": "% of Contribution x Tooling", "type": "percentage"},
        
        {"name": "Total Indirect", "type": "metric"},
        {"name": "% of Contribution x Tooling", "type": "percentage"},
        
        {"name": "Operating Profit/(Loss)", "type": "metric"},
        {"name": "% of Contribution x Tooling", "type": "percentage"},
        
        # Other Income/Expenses
        {"name": "OTHR - Absorption", "type": "account"},
        {"name": "OTHR - Interest Expense", "type": "account"},
        {"name": "OTHR - Misc Income", "type": "account"},
        {"name": "OTHR - Fixed Asset Gain/(Loss)", "type": "account"},
        {"name": "OTHR - Income Tax Expense", "type": "account"},
        {"name": "Total Other Inc/(Exp)", "type": "metric"},
        
        {"name": "Net Income/(Loss)", "type": "metric"},
    ]
    
    # Build the data structure for the template
    financial_data = []
    for item in line_items:
        if item["type"] == "account":
            # Get account data from database for each quarter
            q1_account_data = q1_accounts_dict.get(item["name"])
            q2_account_data = q2_accounts_dict.get(item["name"])
            q2_budget_data = q2_budget_accounts_dict.get(item["name"])
            q2_variance_data = q2_variance_accounts_dict.get(item["name"])
            q2_average_data = q2_average_accounts_dict.get(item["name"])
            q3_budget_data = q3_budget_accounts_dict.get(item["name"])
            
            # Extract values, defaulting to 0 if not found
            q1_val = q1_account_data.get('value', 0) if q1_account_data else 0
            q2_val = q2_account_data.get('value', 0) if q2_account_data else 0
            q2_budget_val = q2_budget_data.get('value', 0) if q2_budget_data else 0
            q2_average_val = q2_average_data.get('avg_value', 0) if q2_average_data else 0
            q3_budget_val = q3_budget_data.get('value', 0) if q3_budget_data else 0
            
            # Get variance from dedicated function
            variance = q2_variance_data.get('variance', 0) if q2_variance_data else 0
            
            financial_data.append({
                "name": item["name"],
                "type": "account", 
                "group": item.get("group"),
                "is_group_header": item.get("is_group_header", False),
                "q1_actual": q1_val,
                "q2_actual": q2_val,
                "q2_budget": q2_budget_val,
                "q2_average": q2_average_val,
                "q3_budget": q3_budget_val,
                "variance": variance,
            })
        elif item["type"] == "metric":
            # Get metric data from database for each quarter
            q1_metric_data = q1_metrics_dict.get(item["name"])
            q2_metric_data = q2_metrics_dict.get(item["name"])
            q2_budget_data = q2_budget_metrics_dict.get(item["name"])
            q2_variance_data = q2_variance_metrics_dict.get(item["name"])
            q2_average_data = q2_average_metrics_dict.get(item["name"])
            q3_budget_data = q3_budget_metrics_dict.get(item["name"])
            
            # Extract values, defaulting to 0 if not found
            q1_val = q1_metric_data.get('value', 0) if q1_metric_data else 0
            q2_val = q2_metric_data.get('value', 0) if q2_metric_data else 0
            q2_budget_val = q2_budget_data.get('value', 0) if q2_budget_data else 0
            q2_average_val = q2_average_data.get('avg_value', 0) if q2_average_data else 0
            q3_budget_val = q3_budget_data.get('value', 0) if q3_budget_data else 0
            
            # Get variance from dedicated function
            variance = q2_variance_data.get('variance', 0) if q2_variance_data else 0
            
            financial_data.append({
                "name": item["name"],
                "type": "metric",
                "group": item.get("group"),
                "is_group_header": item.get("is_group_header", False),
                "q1_actual": q1_val,
                "q2_actual": q2_val,
                "q2_budget": q2_budget_val,
                "q2_average": q2_average_val,
                "q3_budget": q3_budget_val,
                "variance": variance,
            })
        else:  # percentage
            financial_data.append({
                "name": item["name"],
                "type": "percentage",
                "group": item.get("group"),
                "is_group_header": item.get("is_group_header", False),
                "q1_actual": 0,  # Calculate percentages
                "q2_actual": 0,
                "q2_budget": 0,
                "q2_average": 0,
                "q3_budget": 0,
                "variance": 0,
            })
    
    context = {
        "financial_data": financial_data,
    }
    
    return render(request, "dashboard/budget_actual.html", context)

def load_metrics(request):
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    try:
        selected_company = request.session.get('selected_company', 'AFP')
    except AttributeError:
        selected_company = 'AFP'
    company_ids = [selected_company]
    
    # Convert date strings to year/period format
    # For now, assume dates map to periods (this may need adjustment based on your business logic)
    from datetime import datetime
    if start_date and end_date:
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        start_year = start_dt.year
        start_period = start_dt.month  # Assuming month = period
        end_year = end_dt.year
        end_period = end_dt.month  # Assuming month = period
        
        metrics = fetch_actual_metrics(start_year, start_period, end_year, end_period, company_ids)
    else:
        metrics = []
    
    return render(request, "dashboard/_metrics_table.html", {"metrics": metrics})

def load_accounts(request):
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    try:
        selected_company = request.session.get('selected_company', 'AFP')
    except AttributeError:
        selected_company = 'AFP'
    company_ids = [selected_company]
    
    # Convert date strings to year/period format
    # For now, assume dates map to periods (this may need adjustment based on your business logic)
    from datetime import datetime
    if start_date and end_date:
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        start_year = start_dt.year
        start_period = start_dt.month  # Assuming month = period
        end_year = end_dt.year
        end_period = end_dt.month  # Assuming month = period
        
        accounts = fetch_actual_accounts(start_year, start_period, end_year, end_period, company_ids)
    else:
        accounts = []
    
    return render(request, "dashboard/_accounts_table.html", {"accounts": accounts})

def dashboard(request):
    # Get selected company from session, default to AFP
    try:
        selected_company = request.session.get('selected_company', 'AFP')
    except AttributeError:
        selected_company = 'AFP'  # Fallback if session not available
    
    context = {
        'selected_company': selected_company,
        'companies': ['AFP', 'Company1', 'Company2'],  # Add available companies
    }
    return render(request, "dashboard/dashboard.html", context)

def simple_home(request):
    from django.http import HttpResponse
    return HttpResponse("Hello! Django is working. <a href='/budget-vs-actual/'>Go to Budget vs Actual</a>")

def test_styles(request):
    return render(request, "dashboard/test.html")

def test_buttons(request):
    return render(request, "dashboard/test_buttons.html")

def minimal_test(request):
    return render(request, "dashboard/minimal_test.html")

def select_company(request):
    """
    Handle company selection from dropdown
    """
    if request.method == 'POST':
        company_id = request.POST.get('company_id')
        if company_id:
            request.session['selected_company'] = company_id
    
    # Redirect back to the referring page or budget vs actual
    next_url = request.META.get('HTTP_REFERER', '/budget-actual/')
    return redirect(next_url)

def settings(request):
    """
    Settings page for managing current month/year and other app settings
    """
    from datetime import datetime
    
    # Get current settings from session or use defaults
    try:
        selected_company = request.session.get('selected_company', 'AFP')
        current_month = request.session.get('current_month', datetime.now().month)
        current_year = request.session.get('current_year', datetime.now().year)
    except AttributeError:
        selected_company = 'AFP'
        current_month = datetime.now().month
        current_year = datetime.now().year
    
    # Handle form submissions
    if request.method == 'POST':
        if 'update_settings' in request.POST:
            new_month = int(request.POST.get('current_month', current_month))
            new_year = int(request.POST.get('current_year', current_year))
            
            request.session['current_month'] = new_month
            request.session['current_year'] = new_year
            
            # Show success message
            from django.contrib import messages
            messages.success(request, f'Settings updated: {datetime(new_year, new_month, 1).strftime("%B %Y")}')
    
    context = {
        'selected_company': selected_company,
        'companies': ['AFP', 'Company1', 'Company2'],
        'current_month': current_month,
        'current_year': current_year,
        'months': [
            (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
            (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
            (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')
        ],
        'years': list(range(2020, 2030)),
    }
    
    return render(request, "dashboard/settings.html", context)

def roll_month(request):
    """
    Roll to the next month
    """
    from datetime import datetime
    
    if request.method == 'POST':
        try:
            current_month = request.session.get('current_month', datetime.now().month)
            current_year = request.session.get('current_year', datetime.now().year)
            
            # Roll to next month
            if current_month == 12:
                new_month = 1
                new_year = current_year + 1
            else:
                new_month = current_month + 1
                new_year = current_year
            
            request.session['current_month'] = new_month
            request.session['current_year'] = new_year
            
            # Show success message
            from django.contrib import messages
            messages.success(request, f'Rolled to: {datetime(new_year, new_month, 1).strftime("%B %Y")}')
            
        except Exception as e:
            from django.contrib import messages
            messages.error(request, f'Error rolling month: {str(e)}')
    
    return redirect('settings')
