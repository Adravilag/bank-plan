import { Component, OnInit, input, output, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import Plotly from 'plotly.js-dist-min';

export interface ExpenseItem {
  label: string;
  value: number;
  pct: string;
  color: string;
}

@Component({
  selector: 'app-expense-distribution',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './expense-distribution.component.html',
  styleUrl: './expense-distribution.component.scss',
})
export class ExpenseDistributionComponent implements OnInit {
  data = input.required<{ labels: string[]; values: number[] }>();
  totalTransactions = input<number>(0);

  filterChanged = output<string | null>();

  private readonly EXPENSE_COLORS = ['#002e5a', '#004481', '#723101', '#94a3b8', '#1e3a5f'];

  selectedExpenseIndex = signal<number | null>(null);
  hoveredExpenseIndex = signal<number | null>(null);
  expenseItems = signal<ExpenseItem[]>([]);
  activeFilter = signal<string | null>(null);

  activeExpenseItem = computed(() => {
    const hovered = this.hoveredExpenseIndex();
    const selected = this.selectedExpenseIndex();
    const idx = hovered ?? selected;
    const items = this.expenseItems();
    return idx !== null && items[idx] ? items[idx] : null;
  });

  ngOnInit(): void {
    const { labels, values } = this.data();
    if (!labels.length) return;

    const total = values.reduce((a, b) => a + b, 0);
    const items: ExpenseItem[] = labels.map((label, i) => ({
      label,
      value: values[i],
      pct: ((values[i] / total) * 100).toFixed(1) + '%',
      color: this.EXPENSE_COLORS[i] || '#ccc',
    }));
    this.expenseItems.set(items);

    setTimeout(() => this.renderChart(labels, values), 100);
  }

  private renderChart(labels: string[], values: number[]): void {
    Plotly.newPlot(
      'chart-expense',
      [{
        labels,
        values,
        type: 'pie',
        hole: 0.68,
        marker: {
          colors: this.EXPENSE_COLORS.slice(0, labels.length),
          line: { color: labels.map(() => '#fff'), width: labels.map(() => 2) },
        },
        textinfo: 'none',
        hoverinfo: 'none',
        pull: labels.map(() => 0),
        rotation: -40,
        direction: 'clockwise',
        sort: false,
      }],
      {
        paper_bgcolor: 'transparent',
        font: { family: 'Inter', color: '#424750', size: 11 },
        margin: { t: 5, b: 5, l: 5, r: 5 },
        showlegend: false,
      },
      { responsive: true, displayModeBar: false }
    );

    const chartEl = document.getElementById('chart-expense');
    if (chartEl) {
      (chartEl as any).on('plotly_click', (eventData: any) => {
        this.onExpenseClick(eventData.points[0].pointNumber);
      });

      (chartEl as any).on('plotly_hover', (eventData: any) => {
        const idx = eventData.points[0].pointNumber;
        this.hoveredExpenseIndex.set(idx);
        const lineWidths = labels.map((_, i) => i === idx ? 3 : 2);
        const colors = this.EXPENSE_COLORS.slice(0, labels.length).map((c, i) =>
          i === idx ? c : c + 'aa'
        );
        Plotly.restyle('chart-expense', {
          'marker.colors': [colors],
          'marker.line.width': [lineWidths],
        }, [0]);
      });

      (chartEl as any).on('plotly_unhover', () => {
        this.hoveredExpenseIndex.set(null);
        if (this.selectedExpenseIndex() === null) {
          Plotly.restyle('chart-expense', {
            'marker.colors': [this.EXPENSE_COLORS.slice(0, labels.length)],
            'marker.line.width': [labels.map(() => 2)],
          }, [0]);
        }
      });
    }
  }

  onExpenseClick(index: number): void {
    const current = this.selectedExpenseIndex();
    const isDeselect = current === index;
    this.selectedExpenseIndex.set(isDeselect ? null : index);

    const items = this.expenseItems();
    if (!items.length) return;

    const pull = items.map((_, i) => (i === index && !isDeselect ? 0.1 : 0));
    const colors = this.EXPENSE_COLORS.slice(0, items.length).map((c, i) =>
      isDeselect ? c : (i === index ? c : c + '40')
    );

    Plotly.animate('chart-expense', {
      data: [{
        pull,
        marker: {
          colors,
          line: {
            color: items.map(() => '#fff'),
            width: items.map((_, i) => i === index && !isDeselect ? 3 : 2),
          },
        },
      }],
      traces: [0],
      layout: {},
    }, {
      transition: { duration: 400, easing: 'cubic-in-out' },
      frame: { duration: 400, redraw: true },
    });

    const filterLabel = isDeselect ? null : items[index]?.label ?? null;
    this.activeFilter.set(filterLabel);
    this.filterChanged.emit(filterLabel);
  }

  resetFilter(): void {
    this.selectedExpenseIndex.set(null);
    this.activeFilter.set(null);
    this.filterChanged.emit(null);

    const items = this.expenseItems();
    Plotly.animate('chart-expense', {
      data: [{
        pull: items.map(() => 0),
        marker: {
          colors: this.EXPENSE_COLORS.slice(0, items.length),
          line: { color: items.map(() => '#fff'), width: items.map(() => 2) },
        },
      }],
      traces: [0],
      layout: {},
    }, {
      transition: { duration: 400, easing: 'cubic-in-out' },
      frame: { duration: 400, redraw: true },
    });
  }
}
