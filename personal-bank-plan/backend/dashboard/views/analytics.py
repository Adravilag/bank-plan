from rest_framework.decorators import api_view
from rest_framework.response import Response

from ..services import (
    get_dashboard_summary,
    get_transactions_by_type,
    get_transactions_by_month,
    get_balance_by_account_type,
    get_loan_summary,
    get_cash_flow_by_month,
    get_top_accounts,
    get_monthly_growth,
)


@api_view(['GET'])
def dashboard_summary(request):
    """Resumen general del banco para el dashboard principal."""
    return Response(get_dashboard_summary())


@api_view(['GET'])
def transactions_by_type(request):
    """Transacciones agrupadas por tipo."""
    return Response(get_transactions_by_type())


@api_view(['GET'])
def transactions_by_month(request):
    """Transacciones agrupadas por mes."""
    return Response(get_transactions_by_month())


@api_view(['GET'])
def balance_by_account_type(request):
    """Balance total agrupado por tipo de cuenta."""
    return Response(get_balance_by_account_type())


@api_view(['GET'])
def loan_summary(request):
    """Resumen de préstamos por estado."""
    return Response(get_loan_summary())


@api_view(['GET'])
def cash_flow_by_month(request):
    """Flujo de caja mensual con depósitos, retiros y crecimiento."""
    return Response(get_cash_flow_by_month())


@api_view(['GET'])
def top_accounts(request):
    """Top cuentas por balance con métricas adicionales."""
    limit = int(request.query_params.get('limit', 10))
    return Response(get_top_accounts(min(limit, 50)))


@api_view(['GET'])
def monthly_growth(request):
    """Crecimiento mes a mes."""
    return Response(get_monthly_growth())
