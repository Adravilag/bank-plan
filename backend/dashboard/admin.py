from django.contrib import admin
from .models import Account, Transaction, Loan


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('account_number', 'holder_name', 'account_type', 'balance', 'is_active')
    list_filter = ('account_type', 'is_active')
    search_fields = ('holder_name', 'account_number')


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('account', 'transaction_type', 'amount', 'date', 'category')
    list_filter = ('transaction_type', 'category')
    search_fields = ('description',)


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('account', 'amount', 'interest_rate', 'status', 'remaining_balance')
    list_filter = ('status',)
