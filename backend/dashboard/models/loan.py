from django.db import models

from .account import Account


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

    class Meta:
        verbose_name = 'Préstamo'
        verbose_name_plural = 'Préstamos'

    def __str__(self):
        return f"Préstamo €{self.amount} - {self.status}"
