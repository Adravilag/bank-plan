import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule, DatePipe } from '@angular/common';
import { BankService, Transaction } from '../../services/bank.service';

@Component({
  selector: 'app-transactions',
  standalone: true,
  imports: [CommonModule, DatePipe],
  templateUrl: './transactions.component.html',
  styleUrl: './transactions.component.scss',
})
export class TransactionsComponent implements OnInit {
  private bankService = inject(BankService);
  transactions = signal<Transaction[]>([]);

  ngOnInit(): void {
    this.bankService.getTransactions().subscribe((data) => this.transactions.set(data));
  }

  translateType(type: string): string {
    const map: Record<string, string> = {
      deposit: 'Deposit',
      withdrawal: 'Withdrawal',
      transfer: 'Transfer',
      payment: 'Payment',
      fee: 'Fee',
    };
    return map[type] || type;
  }

  formatCurrency(value: number): string {
    return new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(value);
  }
}
