from django.db import models

from .account import Account


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
        verbose_name = 'Transacción'
        verbose_name_plural = 'Transacciones'

    def __str__(self):
        return f"{self.transaction_type} - €{self.amount}"
