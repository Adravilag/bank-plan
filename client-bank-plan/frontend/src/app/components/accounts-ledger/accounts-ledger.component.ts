import { Component, input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Account, TopAccount } from '../../services/bank.service';

@Component({
  selector: 'app-accounts-ledger',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './accounts-ledger.component.html',
  styleUrl: './accounts-ledger.component.scss',
})
export class AccountsLedgerComponent {
  accounts = input.required<Account[]>();
  topAccounts = input<TopAccount[]>([]);

  private maxBalance = 0;

  getBalanceBarWidth(balance: number): number {
    if (!this.maxBalance) {
      const accs = this.accounts();
      this.maxBalance = accs.length ? Math.max(...accs.map(a => a.balance)) : 0;
    }
    return this.maxBalance > 0 ? (balance / this.maxBalance) * 100 : 0;
  }

  formatCurrency(value: number): string {
    return new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(value);
  }

  getAccountTypeLabel(type: string): string {
    const map: Record<string, string> = {
      savings: 'Ahorro',
      checking: 'Corriente',
      credit: 'Crédito',
      investment: 'Inversión',
    };
    return map[type] || type;
  }

  getStatusClass(account: Account): string {
    if (!account.is_active) return 'status-audit';
    if (account.balance > 100000) return 'status-liquid';
    return 'status-stable';
  }

  getStatusLabel(account: Account): string {
    if (!account.is_active) return 'Auditing';
    if (account.balance > 100000) return 'Liquid';
    return 'Stable';
  }

  getTopAccountTxns(accountId: number): string {
    const top = this.topAccounts().find(a => a.id === accountId);
    return top ? top.transaction_count.toLocaleString() : '—';
  }
}
