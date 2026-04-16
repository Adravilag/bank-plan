import { Component, OnInit, AfterViewInit, inject, signal, computed, viewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  BankService,
  DashboardSummary,
  Account,
  LoanSummary,
  TopAccount,
} from '../../services/bank.service';
import { MetricCardComponent } from '../../components/metric-card/metric-card.component';
import { CashFlowChartComponent, CashFlowData } from '../../components/cash-flow-chart/cash-flow-chart.component';
import { ExpenseDistributionComponent } from '../../components/expense-distribution/expense-distribution.component';
import { LiquidityForecastComponent, LiquidityData } from '../../components/liquidity-forecast/liquidity-forecast.component';
import { AccountsLedgerComponent } from '../../components/accounts-ledger/accounts-ledger.component';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    MetricCardComponent,
    CashFlowChartComponent,
    ExpenseDistributionComponent,
    LiquidityForecastComponent,
    AccountsLedgerComponent,
  ],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss',
})
export class DashboardComponent implements OnInit, AfterViewInit {
  private bankService = inject(BankService);

  liquidityChart = viewChild<LiquidityForecastComponent>('liquidityChart');

  summary = signal<DashboardSummary | null>(null);
  accounts = signal<Account[]>([]);
  topAccounts = signal<TopAccount[]>([]);
  loanData = signal<LoanSummary[]>([]);

  cashFlowData = signal<CashFlowData | null>(null);
  expenseData = signal<{ labels: string[]; values: number[] } | null>(null);
  liquidityData = signal<LiquidityData | null>(null);
  sparkBalanceData = signal<number[]>([]);
  sparkTransactionData = signal<number[]>([]);

  balanceTrend = computed(() => {
    const data = this.cashFlowData();
    if (!data || data.totals.length < 2) return 0;
    return data.totals[data.totals.length - 1] - data.totals[data.totals.length - 2];
  });

  loanUtilization = computed(() => {
    const loans = this.loanData();
    const total = loans.reduce((a, b) => a + b.count, 0);
    const active = loans.find(l => l.status === 'active');
    return total > 0 && active ? (active.count / total) * 100 : 0;
  });

  ngOnInit(): void {
    this.bankService.getSummary().subscribe((data) => this.summary.set(data));
    this.bankService.getAccounts().subscribe((data) => this.accounts.set(data.slice(0, 5)));
    this.bankService.getTopAccounts(5).subscribe((data) => this.topAccounts.set(data));
    this.bankService.getLoanSummary().subscribe((data) => this.loanData.set(data));
    this.loadCashFlowData();
    this.loadExpenseData();
    this.loadLiquidityData();
  }

  ngAfterViewInit(): void {
    this.observeScrollAnimations();
  }

  private observeScrollAnimations(): void {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('animate-in');
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.1 }
    );

    setTimeout(() => {
      document.querySelectorAll('.metric-card, .card, .two-col .card').forEach((el) => {
        observer.observe(el);
      });
    }, 100);
  }

  onExpenseFilterChanged(filterLabel: string | null): void {
    this.liquidityChart()?.applyCrossfilter(filterLabel);
  }

  formatCurrency(value: number): string {
    return new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(value);
  }

  private translateType(type: string): string {
    const map: Record<string, string> = {
      deposit: 'Depósito',
      withdrawal: 'Retiro',
      transfer: 'Transferencia',
      payment: 'Pago',
      fee: 'Comisión',
    };
    return map[type] || type;
  }

  private translateAccountType(type: string): string {
    const map: Record<string, string> = {
      savings: 'Ahorro',
      checking: 'Corriente',
      credit: 'Crédito',
      investment: 'Inversión',
    };
    return map[type] || type;
  }

  private loadCashFlowData(): void {
    this.bankService.getTransactionsByMonth().subscribe((data) => {
      const months = data.map((d) => d.month);
      const totals = data.map((d) => d.total);
      const counts = data.map((d) => d.count);

      let cumulative = 0;
      const cashFlow = totals.map((t) => {
        cumulative += t;
        return cumulative;
      });

      this.cashFlowData.set({ months, totals, counts });
      this.sparkBalanceData.set(cashFlow);
      this.sparkTransactionData.set(counts);
    });
  }

  private loadExpenseData(): void {
    this.bankService.getTransactionsByType().subscribe((data) => {
      const labels = data.map((d) => this.translateType(d.transaction_type));
      const values = data.map((d) => d.count);
      this.expenseData.set({ labels, values });
    });
  }

  private loadLiquidityData(): void {
    this.bankService.getBalanceByAccountType().subscribe((data) => {
      const labels = data.map((d) => this.translateAccountType(d.account_type));
      const values = data.map((d) => Number(d.total_balance));
      const counts = data.map((d) => d.count);
      const avgs = data.map((d) => Number(d.avg_balance));
      const maxes = data.map((d) => Number(d.max_balance));
      this.liquidityData.set({ labels, values, counts, avgs, maxes });
    });
  }
}
