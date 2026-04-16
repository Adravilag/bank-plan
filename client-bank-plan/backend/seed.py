"""Seed script to populate the database with demo data."""
import random
from datetime import datetime, date, timedelta, timezone

from app import create_app
from extensions import db
from models import Account, Transaction, Loan


def seed():
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()

        # Create accounts
        accounts_data = [
            ('ES001', 'María García', 'savings', 15000),
            ('ES002', 'Carlos López', 'checking', 8500),
            ('ES003', 'Ana Martínez', 'credit', 3200),
            ('ES004', 'Pedro Sánchez', 'investment', 45000),
            ('ES005', 'Laura Fernández', 'savings', 22000),
            ('ES006', 'Miguel Torres', 'checking', 6700),
            ('ES007', 'Isabel Ruiz', 'savings', 31000),
            ('ES008', 'David Moreno', 'credit', 1800),
            ('ES009', 'Carmen Díaz', 'investment', 67000),
            ('ES010', 'Javier Romero', 'checking', 12400),
        ]

        accounts = []
        for num, name, atype, balance in accounts_data:
            acc = Account(
                account_number=num,
                holder_name=name,
                account_type=atype,
                balance=balance,
                is_active=True,
            )
            db.session.add(acc)
            accounts.append(acc)

        db.session.flush()

        # Create transactions (last 12 months)
        txn_types = ['deposit', 'withdrawal', 'transfer', 'payment', 'fee']
        categories = ['Nómina', 'Alquiler', 'Supermercado', 'Restaurante', 'Transporte',
                       'Servicios', 'Ocio', 'Seguros', 'Educación', 'Salud']
        base_date = datetime.now(timezone.utc)

        for acc in accounts:
            for i in range(random.randint(20, 50)):
                days_ago = random.randint(0, 365)
                txn_date = base_date - timedelta(days=days_ago)
                txn_type = random.choice(txn_types)
                amount = round(random.uniform(10, 5000), 2)

                txn = Transaction(
                    account_id=acc.id,
                    transaction_type=txn_type,
                    amount=amount,
                    description=f'{txn_type.capitalize()} - {random.choice(categories)}',
                    date=txn_date,
                    category=random.choice(categories),
                )
                db.session.add(txn)

        # Create loans
        loan_data = [
            (accounts[0], 10000, 5.5, 24, 458.40, 7500, 'active'),
            (accounts[1], 25000, 4.2, 60, 462.85, 18000, 'active'),
            (accounts[3], 50000, 3.8, 120, 502.23, 42000, 'active'),
            (accounts[4], 8000, 6.0, 12, 688.88, 0, 'paid'),
            (accounts[6], 15000, 5.0, 36, 449.56, 9800, 'active'),
            (accounts[9], 3000, 7.5, 6, 512.50, 3200, 'defaulted'),
        ]

        for acc, amount, rate, term, monthly, remaining, status in loan_data:
            months_ago = random.randint(1, 24)
            loan = Loan(
                account_id=acc.id,
                amount=amount,
                interest_rate=rate,
                term_months=term,
                monthly_payment=monthly,
                remaining_balance=remaining,
                status=status,
                start_date=date.today() - timedelta(days=months_ago * 30),
            )
            db.session.add(loan)

        db.session.commit()
        print(f'Seeded {len(accounts)} accounts, {Transaction.query.count()} transactions, {Loan.query.count()} loans.')


if __name__ == '__main__':
    seed()
