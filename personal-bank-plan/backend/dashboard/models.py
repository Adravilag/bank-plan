from django.db import models


class Account(models.Model):
    ACCOUNT_TYPES = [
        ('savings', 'Cuenta de Ahorro'),
        ('checking', 'Cuenta Corriente'),
        ('credit', 'Tarjeta de Crédito'),
        ('investment', 'Inversión'),
    ]

    account_number = models.CharField(max_length=20, unique=True)
    holder_name = models.CharField(max_length=200)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.holder_name} - {self.account_number}"


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('deposit', 'Depósito'),
        ('withdrawal', 'Retiro'),
        ('transfer', 'Transferencia'),
        ('payment', 'Pago'),
        ('fee', 'Comisión'),
    ]

    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.CharField(max_length=300, blank=True)
    date = models.DateTimeField()
    category = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.transaction_type} - ${self.amount}"


class Loan(models.Model):
    LOAN_STATUS = [
        ('active', 'Activo'),
        ('paid', 'Pagado'),
        ('defaulted', 'En mora'),
    ]

    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='loans')
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    term_months = models.IntegerField()
    monthly_payment = models.DecimalField(max_digits=15, decimal_places=2)
    remaining_balance = models.DecimalField(max_digits=15, decimal_places=2)
    status = models.CharField(max_length=20, choices=LOAN_STATUS, default='active')
    start_date = models.DateField()

    def __str__(self):
        return f"Préstamo ${self.amount} - {self.status}"
