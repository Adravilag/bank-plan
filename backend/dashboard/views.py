from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Account, Transaction, Loan
from .serializers import AccountSerializer, TransactionSerializer, LoanSerializer


class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        account_id = self.request.query_params.get('account')
        if account_id:
            qs = qs.filter(account_id=account_id)
        return qs


class LoanViewSet(viewsets.ModelViewSet):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer


@api_view(['GET'])
def dashboard_summary(request):
    """Resumen general del banco para el dashboard principal."""
    total_accounts = Account.objects.count()
    active_accounts = Account.objects.filter(is_active=True).count()
    total_balance = Account.objects.aggregate(total=Sum('balance'))['total'] or 0
    total_transactions = Transaction.objects.count()
    active_loans = Loan.objects.filter(status='active').count()
    total_loan_amount = Loan.objects.filter(status='active').aggregate(
        total=Sum('remaining_balance')
    )['total'] or 0

    return Response({
        'total_accounts': total_accounts,
        'active_accounts': active_accounts,
        'total_balance': float(total_balance),
        'total_transactions': total_transactions,
        'active_loans': active_loans,
        'total_loan_amount': float(total_loan_amount),
    })


@api_view(['GET'])
def transactions_by_type(request):
    """Transacciones agrupadas por tipo."""
    data = (
        Transaction.objects.values('transaction_type')
        .annotate(count=Count('id'), total=Sum('amount'))
        .order_by('transaction_type')
    )
    return Response(list(data))


@api_view(['GET'])
def transactions_by_month(request):
    """Transacciones agrupadas por mes."""
    data = (
        Transaction.objects.annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(count=Count('id'), total=Sum('amount'))
        .order_by('month')
    )
    result = [
        {'month': item['month'].strftime('%Y-%m'), 'count': item['count'], 'total': float(item['total'])}
        for item in data
    ]
    return Response(result)


@api_view(['GET'])
def balance_by_account_type(request):
    """Balance total agrupado por tipo de cuenta."""
    data = (
        Account.objects.values('account_type')
        .annotate(total_balance=Sum('balance'), count=Count('id'))
        .order_by('account_type')
    )
    return Response(list(data))


@api_view(['GET'])
def loan_summary(request):
    """Resumen de préstamos por estado."""
    data = (
        Loan.objects.values('status')
        .annotate(count=Count('id'), total=Sum('amount'))
        .order_by('status')
    )
    return Response(list(data))
