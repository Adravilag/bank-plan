from decimal import Decimal

from django.db.models import Sum, Count, Avg, Max, Min, Q, F, Case, When, Value, CharField, DecimalField
from django.db.models.functions import TruncMonth

from ..models import Account, Transaction, Loan


def get_dashboard_summary():
    """Calcula los KPIs principales del banco."""
    total_accounts = Account.objects.count()
    active_accounts = Account.objects.filter(is_active=True).count()
    total_balance = Account.objects.aggregate(total=Sum('balance'))['total'] or 0
    total_transactions = Transaction.objects.count()
    active_loans = Loan.objects.filter(status='active').count()
    total_loans = Loan.objects.count()
    total_loan_amount = Loan.objects.filter(status='active').aggregate(
        total=Sum('remaining_balance')
    )['total'] or 0

    return {
        'total_accounts': total_accounts,
        'active_accounts': active_accounts,
        'total_balance': float(total_balance),
        'total_transactions': total_transactions,
        'active_loans': active_loans,
        'total_loans': total_loans,
        'total_loan_amount': float(total_loan_amount),
    }


def get_transactions_by_type():
    """Agrupa transacciones por tipo con conteo y suma."""
    return list(
        Transaction.objects.values('transaction_type')
        .annotate(count=Count('id'), total=Sum('amount'))
        .order_by('transaction_type')
    )


def get_transactions_by_month():
    """Agrupa transacciones por mes con conteo y suma."""
    data = (
        Transaction.objects.annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(count=Count('id'), total=Sum('amount'))
        .order_by('month')
    )
    return [
        {
            'month': item['month'].strftime('%Y-%m'),
            'count': item['count'],
            'total': float(item['total']),
        }
        for item in data
    ]


def get_balance_by_account_type():
    """Calcula balance total agrupado por tipo de cuenta."""
    return list(
        Account.objects.values('account_type')
        .annotate(
            total_balance=Sum('balance'),
            count=Count('id'),
            avg_balance=Avg('balance'),
            max_balance=Max('balance'),
            min_balance=Min('balance'),
        )
        .order_by('account_type')
    )


def get_loan_summary():
    """Resumen de préstamos agrupados por estado."""
    return list(
        Loan.objects.values('status')
        .annotate(
            count=Count('id'),
            total=Sum('amount'),
            avg_rate=Avg('interest_rate'),
            total_remaining=Sum('remaining_balance'),
        )
        .order_by('status')
    )


def get_cash_flow_by_month():
    """Flujo de caja mensual: depósitos vs retiros separados."""
    months = (
        Transaction.objects.annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(
            deposits=Sum(
                Case(
                    When(transaction_type='deposit', then=F('amount')),
                    default=Value(0),
                    output_field=DecimalField(),
                )
            ),
            withdrawals=Sum(
                Case(
                    When(transaction_type='withdrawal', then=F('amount')),
                    default=Value(0),
                    output_field=DecimalField(),
                )
            ),
            transfers=Sum(
                Case(
                    When(transaction_type='transfer', then=F('amount')),
                    default=Value(0),
                    output_field=DecimalField(),
                )
            ),
            payments=Sum(
                Case(
                    When(transaction_type='payment', then=F('amount')),
                    default=Value(0),
                    output_field=DecimalField(),
                )
            ),
            total=Sum('amount'),
            count=Count('id'),
        )
        .order_by('month')
    )

    results = []
    prev_total = None
    for item in months:
        total = float(item['total'])
        growth = None
        if prev_total and prev_total != 0:
            growth = round(((total - prev_total) / prev_total) * 100, 2)
        net = float(item['deposits']) - float(item['withdrawals'])
        results.append({
            'month': item['month'].strftime('%Y-%m'),
            'deposits': float(item['deposits']),
            'withdrawals': float(item['withdrawals']),
            'transfers': float(item['transfers']),
            'payments': float(item['payments']),
            'net_flow': net,
            'total': total,
            'count': item['count'],
            'growth_pct': growth,
        })
        prev_total = total

    return results


def get_top_accounts(limit=10):
    """Top cuentas por balance."""
    accounts = (
        Account.objects.filter(is_active=True)
        .annotate(
            transaction_count=Count('transactions'),
            total_deposited=Sum(
                Case(
                    When(transactions__transaction_type='deposit', then=F('transactions__amount')),
                    default=Value(0),
                    output_field=DecimalField(),
                )
            ),
        )
        .order_by('-balance')[:limit]
    )
    return [
        {
            'id': acc.id,
            'account_number': acc.account_number,
            'holder_name': acc.holder_name,
            'account_type': acc.account_type,
            'balance': float(acc.balance),
            'transaction_count': acc.transaction_count,
            'total_deposited': float(acc.total_deposited or 0),
        }
        for acc in accounts
    ]


def get_monthly_growth():
    """Crecimiento mes a mes del balance total de cuentas."""
    data = get_transactions_by_month()
    if len(data) < 2:
        return {'current': 0, 'previous': 0, 'change': 0, 'change_pct': 0}

    current = data[-1]['total']
    previous = data[-2]['total']
    change = current - previous
    change_pct = round((change / previous) * 100, 2) if previous else 0

    return {
        'current_month': data[-1]['month'],
        'previous_month': data[-2]['month'],
        'current': current,
        'previous': previous,
        'change': change,
        'change_pct': change_pct,
    }
