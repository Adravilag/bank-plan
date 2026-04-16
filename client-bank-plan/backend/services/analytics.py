from sqlalchemy import func, case, extract

from extensions import db
from models import Account, Transaction, Loan


def get_dashboard_summary():
    total_accounts = db.session.query(func.count(Account.id)).scalar()
    active_accounts = db.session.query(func.count(Account.id)).filter(Account.is_active.is_(True)).scalar()
    total_balance = db.session.query(func.coalesce(func.sum(Account.balance), 0)).scalar()
    total_transactions = db.session.query(func.count(Transaction.id)).scalar()
    active_loans = db.session.query(func.count(Loan.id)).filter(Loan.status == 'active').scalar()
    total_loans = db.session.query(func.count(Loan.id)).scalar()
    total_loan_amount = db.session.query(
        func.coalesce(func.sum(Loan.remaining_balance), 0)
    ).filter(Loan.status == 'active').scalar()

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
    rows = (
        db.session.query(
            Transaction.transaction_type,
            func.count(Transaction.id).label('count'),
            func.sum(Transaction.amount).label('total'),
        )
        .group_by(Transaction.transaction_type)
        .order_by(Transaction.transaction_type)
        .all()
    )
    return [
        {'transaction_type': r.transaction_type, 'count': r.count, 'total': float(r.total)}
        for r in rows
    ]


def get_transactions_by_month():
    # Use strftime for SQLite compatibility
    rows = (
        db.session.query(
            func.strftime('%Y-%m', Transaction.date).label('month'),
            func.count(Transaction.id).label('count'),
            func.sum(Transaction.amount).label('total'),
        )
        .group_by('month')
        .order_by('month')
        .all()
    )
    return [
        {'month': r.month, 'count': r.count, 'total': float(r.total)}
        for r in rows
    ]


def get_balance_by_account_type():
    rows = (
        db.session.query(
            Account.account_type,
            func.sum(Account.balance).label('total_balance'),
            func.count(Account.id).label('count'),
            func.avg(Account.balance).label('avg_balance'),
            func.max(Account.balance).label('max_balance'),
            func.min(Account.balance).label('min_balance'),
        )
        .group_by(Account.account_type)
        .order_by(Account.account_type)
        .all()
    )
    return [
        {
            'account_type': r.account_type,
            'total_balance': float(r.total_balance),
            'count': r.count,
            'avg_balance': float(r.avg_balance),
            'max_balance': float(r.max_balance),
            'min_balance': float(r.min_balance),
        }
        for r in rows
    ]


def get_loan_summary():
    rows = (
        db.session.query(
            Loan.status,
            func.count(Loan.id).label('count'),
            func.sum(Loan.amount).label('total'),
            func.avg(Loan.interest_rate).label('avg_rate'),
            func.sum(Loan.remaining_balance).label('total_remaining'),
        )
        .group_by(Loan.status)
        .order_by(Loan.status)
        .all()
    )
    return [
        {
            'status': r.status,
            'count': r.count,
            'total': float(r.total),
            'avg_rate': float(r.avg_rate),
            'total_remaining': float(r.total_remaining),
        }
        for r in rows
    ]


def get_cash_flow_by_month():
    month_col = func.strftime('%Y-%m', Transaction.date).label('month')
    rows = (
        db.session.query(
            month_col,
            func.sum(case(
                (Transaction.transaction_type == 'deposit', Transaction.amount),
                else_=0,
            )).label('deposits'),
            func.sum(case(
                (Transaction.transaction_type == 'withdrawal', Transaction.amount),
                else_=0,
            )).label('withdrawals'),
            func.sum(case(
                (Transaction.transaction_type == 'transfer', Transaction.amount),
                else_=0,
            )).label('transfers'),
            func.sum(case(
                (Transaction.transaction_type == 'payment', Transaction.amount),
                else_=0,
            )).label('payments'),
            func.sum(Transaction.amount).label('total'),
            func.count(Transaction.id).label('count'),
        )
        .group_by('month')
        .order_by('month')
        .all()
    )

    results = []
    prev_total = None
    for r in rows:
        total = float(r.total)
        deposits = float(r.deposits)
        withdrawals = float(r.withdrawals)
        growth = None
        if prev_total and prev_total != 0:
            growth = round(((total - prev_total) / prev_total) * 100, 2)
        results.append({
            'month': r.month,
            'deposits': deposits,
            'withdrawals': withdrawals,
            'transfers': float(r.transfers),
            'payments': float(r.payments),
            'net_flow': deposits - withdrawals,
            'total': total,
            'count': r.count,
            'growth_pct': growth,
        })
        prev_total = total

    return results


def get_top_accounts(limit=10):
    accounts = (
        db.session.query(
            Account,
            func.count(Transaction.id).label('transaction_count'),
            func.coalesce(
                func.sum(case(
                    (Transaction.transaction_type == 'deposit', Transaction.amount),
                    else_=0,
                )),
                0,
            ).label('total_deposited'),
        )
        .outerjoin(Transaction, Account.id == Transaction.account_id)
        .filter(Account.is_active.is_(True))
        .group_by(Account.id)
        .order_by(Account.balance.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            'id': acc.id,
            'account_number': acc.account_number,
            'holder_name': acc.holder_name,
            'account_type': acc.account_type,
            'balance': float(acc.balance),
            'transaction_count': txn_count,
            'total_deposited': float(total_dep),
        }
        for acc, txn_count, total_dep in accounts
    ]


def get_monthly_growth():
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
