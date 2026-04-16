import { Injectable, signal, OnDestroy } from '@angular/core';
import { io, Socket } from 'socket.io-client';

const WS_URL = 'http://localhost:8000';
const NAMESPACE = '/dashboard';

export interface DashboardUpdate {
  summary: {
    total_accounts: number;
    active_accounts: number;
    total_balance: number;
    total_transactions: number;
    active_loans: number;
    total_loans: number;
    total_loan_amount: number;
  };
  cash_flow: {
    month: string;
    deposits: number;
    withdrawals: number;
    net_flow: number;
    total: number;
    count: number;
    growth_pct: number | null;
  }[];
}

export interface ChartDataEvent {
  chart: string;
  data: unknown;
}

@Injectable({ providedIn: 'root' })
export class WebSocketService implements OnDestroy {
  private socket: Socket | null = null;

  connected = signal(false);
  dashboardUpdate = signal<DashboardUpdate | null>(null);
  chartData = signal<ChartDataEvent | null>(null);
  transactionCreated = signal<unknown>(null);

  connect(): void {
    if (this.socket?.connected) return;

    this.socket = io(`${WS_URL}${NAMESPACE}`, {
      transports: ['websocket', 'polling'],
    });

    this.socket.on('connect', () => {
      this.connected.set(true);
    });

    this.socket.on('disconnect', () => {
      this.connected.set(false);
    });

    this.socket.on('dashboard_update', (data: DashboardUpdate) => {
      this.dashboardUpdate.set(data);
    });

    this.socket.on('chart_data', (data: ChartDataEvent) => {
      this.chartData.set(data);
    });

    this.socket.on('transaction_created', (data: unknown) => {
      this.transactionCreated.set(data);
    });
  }

  requestUpdate(): void {
    this.socket?.emit('request_update');
  }

  requestChart(chart: string): void {
    this.socket?.emit('request_chart', { chart });
  }

  disconnect(): void {
    this.socket?.disconnect();
    this.socket = null;
    this.connected.set(false);
  }

  ngOnDestroy(): void {
    this.disconnect();
  }
}
