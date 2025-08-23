import sys, os
sys.path.append(os.path.dirname(__file__))  # add current folder to sys.path

import finance_functions as ff


def main():
    print("=== Testing Finance Functions ===")

    company_ids = ["AFP"]
    components = ["Sales - Aluminum", "MAINT - DC Machines"]
    metrics = ["Net Sales", "Gross Sales"]

    # Actuals
    print("\n--- actual_account ---")
    print(ff.actual_account(2025, 3, 2025, 5, company_ids, components))

    print("\n--- actual_account_average ---")
    print(ff.actual_account_average(2025, 3, 2025, 5, company_ids, components))

    print("\n--- actual_transaction ---")
    print(ff.actual_transaction(2025, 3, 2025, 5, company_ids, components))

    print("\n--- actual_metric ---")
    print(ff.actual_metric(2025, 3, 2025, 5, company_ids, metrics))

    print("\n--- actual_metric_average ---")
    print(ff.actual_metric_average(2025, 3, 2025, 4, company_ids, metrics))

    # Budgets
    print("\n--- budget_account ---")
    print(ff.budget_account(2025, 3, 2025, 5, company_ids, components))

    print("\n--- budget_metric ---")
    print(ff.budget_metric(2025, 3, 2025, 4, company_ids, metrics))

    print("\n--- budget_vs_actual_account ---")
    print(ff.budget_vs_actual_account(2025, 3, 2025, 5, company_ids, components))

    print("\n--- budget_vs_actual_metric ---")
    print(ff.budget_vs_actual_metric(2025, 3, 2025, 5, company_ids, metrics))

if __name__ == "__main__":
    main()
