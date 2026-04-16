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

    class Meta:
        verbose_name = 'Cuenta'
        verbose_name_plural = 'Cuentas'

    def __str__(self):
        return f"{self.holder_name} - {self.account_number}"
