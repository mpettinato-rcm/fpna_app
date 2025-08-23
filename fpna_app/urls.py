from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("budget-vs-actual/", views.budget_vs_actual, name="budget_vs_actual"),
    path("load-metrics/", views.load_metrics, name="load_metrics"),
    path("load-accounts/", views.load_accounts, name="load_accounts"),
    path("select-company/", views.select_company, name="select_company"),
    path("settings/", views.settings, name="settings"),
    path("roll-month/", views.roll_month, name="roll_month"),
]
