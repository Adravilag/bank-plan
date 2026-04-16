import { Component, OnInit, input, output, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import Plotly from 'plotly.js-dist-min';

export interface CashFlowData {
  months: string[];
  totals: number[];
  counts: number[];
}

@Component({
  selector: 'app-cash-flow-chart',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './cash-flow-chart.component.html',
  styleUrl: './cash-flow-chart.component.scss',
})
export class CashFlowChartComponent implements OnInit {
  data = input.required<CashFlowData>();

  activeToggle = signal<string>('12M');
  activeTool = signal<string>('zoom');
  private cashFlowData: { months: string[]; cashFlow: number[]; totals: number[] } | null = null;

  ngOnInit(): void {
    const raw = this.data();
    if (!raw.months.length) return;

    const { months, totals } = raw;
    let cumulative = 0;
    const cashFlow = totals.map((t) => {
      cumulative += t;
      return cumulative;
    });

    this.cashFlowData = { months, cashFlow, totals };

    const zeros = cashFlow.map(() => 0);

    setTimeout(() => {
      Plotly.newPlot(
        'chart-cashflow',
        [
          {
            x: months,
            y: zeros,
            type: 'bar',
            name: 'Neto Mensual',
            yaxis: 'y2',
            marker: {
              color: totals.map(t =>
                t >= 0 ? 'rgba(0, 102, 68, 0.3)' : 'rgba(220, 38, 38, 0.3)'
              ),
              line: {
                color: totals.map(t =>
                  t >= 0 ? 'rgba(0, 102, 68, 0.6)' : 'rgba(220, 38, 38, 0.6)'
                ),
                width: 1,
              },
            },
            hovertemplate:
              '<b>%{x}</b><br>Neto: <b>€%{y:,.0f}</b><extra></extra>',
          },
          {
            x: months,
            y: zeros,
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Acumulado',
            fill: 'tozeroy',
            line: { color: '#004481', width: 3, shape: 'spline' },
            marker: { color: '#004481', size: 8 },
            fillcolor: 'rgba(0, 68, 129, 0.08)',
            hovertemplate:
              '<b>%{x}</b><br>Acumulado: <b>€%{y:,.0f}</b><extra></extra>',
          },
        ],
        {
          paper_bgcolor: 'transparent',
          plot_bgcolor: 'transparent',
          font: { family: 'Inter', color: '#424750', size: 11 },
          margin: { t: 10, b: 40, l: 70, r: 70 },
          xaxis: {
            gridcolor: '#f0f0f0',
            linecolor: '#e2e2e2',
            type: 'category',
            showspikes: true,
            spikemode: 'across',
            spikethickness: 1,
            spikecolor: '#cbd5e1',
            spikedash: 'dot',
            spikesnap: 'cursor',
          },
          yaxis: {
            gridcolor: '#f0f0f0',
            linecolor: '#e2e2e2',
            tickprefix: '€',
            tickformat: ',.0f',
            range: [0, Math.max(...cashFlow) * 1.12],
            title: { text: 'Acumulado', font: { size: 10, color: '#94a3b8' }, standoff: 8 },
            showspikes: true,
            spikemode: 'across',
            spikethickness: 1,
            spikecolor: '#cbd5e1',
            spikedash: 'dot',
          },
          yaxis2: {
            overlaying: 'y',
            side: 'right',
            gridcolor: 'transparent',
            tickprefix: '€',
            tickformat: ',.0f',
            range: [Math.min(0, ...totals) * 1.3, Math.max(...totals) * 1.3],
            title: { text: 'Neto', font: { size: 10, color: '#94a3b8' }, standoff: 8 },
            showgrid: false,
          },
          hoverlabel: {
            bgcolor: '#fff',
            bordercolor: '#c2c6d2',
            font: { family: 'Inter', color: '#002e5a', size: 13 },
          },
          hovermode: 'x unified',
          showlegend: true,
          legend: {
            orientation: 'h',
            y: -0.15,
            x: 0.5,
            xanchor: 'center',
            font: { size: 11, color: '#64748b' },
          },
          bargap: 0.4,
          dragmode: 'zoom',
        },
        {
          responsive: true,
          displayModeBar: false,
        }
      );

      setTimeout(() => {
        Plotly.animate('chart-cashflow', {
          data: [{ y: totals }, { y: cashFlow }],
          traces: [0, 1],
          layout: {},
        }, {
          transition: { duration: 1200, easing: 'cubic-in-out' },
          frame: { duration: 1200, redraw: true },
        });
      }, 300);

      const el = document.getElementById('chart-cashflow');
      if (el) {
        (el as any).on('plotly_doubleclick', () => {
          Plotly.relayout('chart-cashflow', {
            'xaxis.autorange': true,
            'yaxis.range': [0, Math.max(...cashFlow) * 1.12],
            'yaxis2.range': [Math.min(0, ...totals) * 1.3, Math.max(...totals) * 1.3],
          });
        });
      }
    }, 100);
  }

  toggleView(view: string): void {
    this.activeToggle.set(view);
    if (!this.cashFlowData) return;

    const { months, cashFlow, totals } = this.cashFlowData;
    let filteredMonths: string[];
    let filteredCashFlow: number[];
    let filteredTotals: number[];

    if (view === '6M') {
      filteredMonths = months.slice(-6);
      filteredCashFlow = cashFlow.slice(-6);
      filteredTotals = totals.slice(-6);
    } else if (view === '3M') {
      filteredMonths = months.slice(-3);
      filteredCashFlow = cashFlow.slice(-3);
      filteredTotals = totals.slice(-3);
    } else {
      filteredMonths = months;
      filteredCashFlow = cashFlow;
      filteredTotals = totals;
    }

    Plotly.animate('chart-cashflow', {
      data: [
        { x: filteredMonths, y: filteredTotals },
        { x: filteredMonths, y: filteredCashFlow },
      ],
      traces: [0, 1],
      layout: {
        yaxis: { range: [0, Math.max(...filteredCashFlow) * 1.12] },
        yaxis2: { range: [Math.min(0, ...filteredTotals) * 1.3, Math.max(...filteredTotals) * 1.3] },
      },
    }, {
      transition: { duration: 800, easing: 'cubic-in-out' },
      frame: { duration: 800, redraw: true },
    });
  }

  setTool(tool: string): void {
    this.activeTool.set(tool);
    Plotly.relayout('chart-cashflow', { dragmode: tool });
  }

  resetZoom(): void {
    if (!this.cashFlowData) return;
    const { cashFlow, totals } = this.cashFlowData;
    Plotly.relayout('chart-cashflow', {
      'xaxis.autorange': true,
      'yaxis.range': [0, Math.max(...cashFlow) * 1.12],
      'yaxis2.range': [Math.min(0, ...totals) * 1.3, Math.max(...totals) * 1.3],
    });
  }
}
