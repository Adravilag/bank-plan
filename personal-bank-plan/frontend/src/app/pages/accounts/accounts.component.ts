import { Component, OnInit, inject, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { BankService, Account } from '../../services/bank.service';

@Component({
  selector: 'app-accounts',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './accounts.component.html',
  styleUrl: './accounts.component.scss',
})
export class AccountsComponent implements OnInit {
  private bankService = inject(BankService);
  accounts = signal<Account[]>([]);
  activeCount = computed(() => this.accounts().filter(a => a.is_active).length);

  ngOnInit(): void {
    this.bankService.getAccounts().subscribe((data) => this.accounts.set(data));
  }

  translateType(type: string): string {
    const map: Record<string, string> = {
      savings: 'Savings',
      checking: 'Checking',
      credit: 'Credit',
      investment: 'Investment',
    };
    return map[type] || type;
  }

  formatCurrency(value: number): string {
    return new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(value);
  }
}
