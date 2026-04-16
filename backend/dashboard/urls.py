from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'accounts', views.AccountViewSet)
router.register(r'transactions', views.TransactionViewSet)
router.register(r'loans', views.LoanViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/login/', views.login_view, name='login'),
    path('dashboard/summary/', views.dashboard_summary, name='dashboard-summary'),
    path('dashboard/transactions-by-type/', views.transactions_by_type, name='transactions-by-type'),
    path('dashboard/transactions-by-month/', views.transactions_by_month, name='transactions-by-month'),
    path('dashboard/balance-by-account-type/', views.balance_by_account_type, name='balance-by-account-type'),
    path('dashboard/loan-summary/', views.loan_summary, name='loan-summary'),
    path('dashboard/cash-flow/', views.cash_flow_by_month, name='cash-flow'),
    path('dashboard/top-accounts/', views.top_accounts, name='top-accounts'),
    path('dashboard/monthly-growth/', views.monthly_growth, name='monthly-growth'),
]
