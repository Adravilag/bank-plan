import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

const API = 'http://localhost:8000/api';

export interface DashboardSummary {
  total_accounts: number;
  active_accounts: number;
  total_balance: number;
  total_transactions: number;
  active_loans: number;
  total_loans: number;
  total_loan_amount: number;
}

export interface TransactionByType {
  transaction_type: string;
  count: number;
  total: number;
}

export interface TransactionByMonth {
  month: string;
  count: number;
  total: number;
}

export interface BalanceByType {
  account_type: string;
  total_balance: number;
  count: number;
  avg_balance: number;
  max_balance: number;
  min_balance: number;
}

export interface LoanSummary {
  status: string;
  count: number;
  total: number;
  avg_rate: number;
  total_remaining: number;
}

export interface CashFlowMonth {
  month: string;
  deposits: number;
  withdrawals: number;
  transfers: number;
  payments: number;
  net_flow: number;
  total: number;
  count: number;
  growth_pct: number | null;
}

export interface TopAccount {
  id: number;
  account_number: string;
  holder_name: string;
  account_type: string;
  balance: number;
  transaction_count: number;
  total_deposited: number;
}

export interface MonthlyGrowth {
  current_month: string;
  previous_month: string;
  current: number;
  previous: number;
  change: number;
  change_pct: number;
}

export interface Account {
  id: number;
  account_number: string;
  holder_name: string;
  account_type: string;
  balance: number;
  is_active: boolean;
  created_at: string;
}

export interface Transaction {
  id: number;
  account: number;
  transaction_type: string;
  amount: number;
  description: string;
  date: string;
  category: string;
}

@Injectable({ providedIn: 'root' })
export class BankService {
  private http = inject(HttpClient);

  getSummary(): Observable<DashboardSummary> {
    return this.http.get<DashboardSummary>(`${API}/dashboard/summary/`);
  }

  getTransactionsByType(): Observable<TransactionByType[]> {
    return this.http.get<TransactionByType[]>(`${API}/dashboard/transactions-by-type/`);
  }

  getTransactionsByMonth(): Observable<TransactionByMonth[]> {
    return this.http.get<TransactionByMonth[]>(`${API}/dashboard/transactions-by-month/`);
  }

  getBalanceByAccountType(): Observable<BalanceByType[]> {
    return this.http.get<BalanceByType[]>(`${API}/dashboard/balance-by-account-type/`);
  }

  getLoanSummary(): Observable<LoanSummary[]> {
    return this.http.get<LoanSummary[]>(`${API}/dashboard/loan-summary/`);
  }

  getAccounts(): Observable<Account[]> {
    return this.http.get<Account[]>(`${API}/accounts/`);
  }

  getTransactions(): Observable<Transaction[]> {
    return this.http.get<Transaction[]>(`${API}/transactions/`);
  }

  getCashFlow(): Observable<CashFlowMonth[]> {
    return this.http.get<CashFlowMonth[]>(`${API}/dashboard/cash-flow/`);
  }

  getTopAccounts(limit = 10): Observable<TopAccount[]> {
    return this.http.get<TopAccount[]>(`${API}/dashboard/top-accounts/?limit=${limit}`);
  }

  getMonthlyGrowth(): Observable<MonthlyGrowth> {
    return this.http.get<MonthlyGrowth>(`${API}/dashboard/monthly-growth/`);
  }
}
