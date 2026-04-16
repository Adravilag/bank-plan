import random
from datetime import datetime, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from dashboard.models import Account, Transaction, Loan


class Command(BaseCommand):
    help = 'Genera datos de prueba para el dashboard bancario'

    def handle(self, *args, **options):
        self.stdout.write('Limpiando datos existentes...')
        Transaction.objects.all().delete()
        Loan.objects.all().delete()
        Account.objects.all().delete()

        names = [
            'Carlos García', 'María López', 'Juan Martínez', 'Ana Rodríguez',
            'Pedro Sánchez', 'Laura Fernández', 'Miguel Torres', 'Sofía Ruiz',
            'Diego Herrera', 'Valentina Castro', 'Andrés Morales', 'Camila Vargas',
            'Luis Ramírez', 'Isabella Flores', 'Mateo Jiménez', 'Daniela Reyes',
            'Sebastián Díaz', 'Paula Mendoza', 'Nicolás Ortiz', 'Gabriela Romero',
        ]
        account_types = ['savings', 'checking', 'credit', 'investment']
        transaction_types = ['deposit', 'withdrawal', 'transfer', 'payment', 'fee']
        categories = [
            'Nómina', 'Alimentos', 'Transporte', 'Servicios', 'Entretenimiento',
            'Educación', 'Salud', 'Inversión', 'Ahorro', 'Otros',
        ]

        accounts = []
        for i, name in enumerate(names):
            acc = Account.objects.create(
                account_number=f'100{i:04d}{random.randint(1000, 9999)}',
                holder_name=name,
                account_type=random.choice(account_types),
                balance=Decimal(str(round(random.uniform(1000, 500000), 2))),
                is_active=random.random() > 0.1,
            )
            accounts.append(acc)

        self.stdout.write(f'Creadas {len(accounts)} cuentas')

        # Transactions over the last 12 months
        now = timezone.now()
        transactions = []
        for _ in range(500):
            days_ago = random.randint(0, 365)
            tx_date = now - timedelta(days=days_ago, hours=random.randint(0, 23))
            tx_type = random.choice(transaction_types)
            amount = Decimal(str(round(random.uniform(10, 50000), 2)))

            transactions.append(Transaction(
                account=random.choice(accounts),
                transaction_type=tx_type,
                amount=amount,
                description=f'{tx_type.capitalize()} automático',
                date=tx_date,
                category=random.choice(categories),
            ))

        Transaction.objects.bulk_create(transactions)
        self.stdout.write(f'Creadas {len(transactions)} transacciones')

        # Loans
        loan_count = 0
        for acc in random.sample(accounts, 10):
            amount = Decimal(str(round(random.uniform(5000, 200000), 2)))
            rate = Decimal(str(round(random.uniform(5, 18), 2)))
            term = random.choice([12, 24, 36, 48, 60])
            monthly = amount * (1 + rate / 100) / term
            status = random.choice(['active', 'active', 'active', 'paid', 'defaulted'])
            remaining = amount * Decimal(str(random.uniform(0.1, 0.9))) if status == 'active' else Decimal('0')

            Loan.objects.create(
                account=acc,
                amount=amount,
                interest_rate=rate,
                term_months=term,
                monthly_payment=round(monthly, 2),
                remaining_balance=round(remaining, 2),
                status=status,
                start_date=now.date() - timedelta(days=random.randint(30, 730)),
            )
            loan_count += 1

        self.stdout.write(f'Creados {loan_count} préstamos')
        self.stdout.write(self.style.SUCCESS('Datos de prueba generados correctamente'))
