import { Component, OnInit, input, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import Plotly from 'plotly.js-dist-min';

export interface LiquidityData {
  labels: string[];
  values: number[];
  counts: number[];
  avgs: number[];
  maxes: number[];
}

@Component({
  selector: 'app-liquidity-forecast',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './liquidity-forecast.component.html',
  styleUrl: './liquidity-forecast.component.scss',
})
export class LiquidityForecastComponent implements OnInit {
  data = input.required<LiquidityData>();

  private readonly BAR_COLORS = ['#002e5a', '#004481', '#1e3a5f', '#0d6efd'];

  ngOnInit(): void {
    const { labels, values, counts, avgs, maxes } = this.data();
    if (!labels.length) return;

    const zeros = values.map(() => 0);
    const total = values.reduce((a, b) => a + b, 0);

    setTimeout(() => {
      Plotly.newPlot(
        'chart-liquidity',
        [{
          x: labels,
          y: zeros,
          type: 'bar',
          marker: {
            color: this.BAR_COLORS.slice(0, labels.length),
            line: { width: 0 },
            opacity: 0.9,
          },
          text: values.map(v => '€' + v.toLocaleString('en-US', { maximumFractionDigits: 0 })),
          textposition: 'outside',
          textfont: { size: 10, color: '#64748b', family: 'Inter' },
          customdata: counts.map((c, i) => [
            c,
            ((values[i] / total) * 100).toFixed(1),
            '€' + avgs[i].toLocaleString('en-US', { maximumFractionDigits: 0 }),
            '€' + maxes[i].toLocaleString('en-US', { maximumFractionDigits: 0 }),
          ]),
          hovertemplate:
            '<b>%{x}</b><br>' +
            'Balance: <b>€%{y:,.0f}</b><br>' +
            'Cuentas: %{customdata[0]}<br>' +
            'Promedio: %{customdata[2]}<br>' +
            'Mayor: %{customdata[3]}<br>' +
            'Participación: %{customdata[1]}%<extra></extra>',
        }],
        {
          paper_bgcolor: 'transparent',
          plot_bgcolor: 'transparent',
          font: { family: 'Inter', color: '#424750', size: 11 },
          margin: { t: 30, b: 40, l: 70, r: 20 },
          xaxis: { gridcolor: 'transparent' },
          yaxis: {
            gridcolor: '#f0f0f0',
            tickprefix: '€',
            tickformat: ',.0f',
            range: [0, Math.max(...values) * 1.25],
            zeroline: true,
            zerolinecolor: '#e2e8f0',
          },
          bargap: 0.35,
          hoverlabel: {
            bgcolor: '#fff',
            bordercolor: '#c2c6d2',
            font: { family: 'Inter', color: '#002e5a', size: 12 },
          },
          dragmode: false,
        },
        { responsive: true, displayModeBar: false }
      );

      setTimeout(() => {
        Plotly.animate('chart-liquidity', {
          data: [{ y: values }],
          traces: [0],
          layout: {},
        }, {
          transition: { duration: 1000, easing: 'cubic-in-out' },
          frame: { duration: 1000, redraw: true },
        });
      }, 600);

      const chartEl = document.getElementById('chart-liquidity');
      if (chartEl) {
        (chartEl as any).on('plotly_hover', (eventData: any) => {
          const pointIndex = eventData.points[0].pointNumber;
          const colors = this.BAR_COLORS.slice(0, labels.length).map((c, i) =>
            i === pointIndex ? c : c + '30'
          );
          Plotly.restyle('chart-liquidity', { 'marker.color': [colors] }, [0]);
        });

        (chartEl as any).on('plotly_unhover', () => {
          Plotly.restyle('chart-liquidity', {
            'marker.color': [this.BAR_COLORS.slice(0, labels.length)],
          }, [0]);
        });

        (chartEl as any).on('plotly_click', (eventData: any) => {
          const pt = eventData.points[0];
          Plotly.relayout('chart-liquidity', {
            annotations: [{
              x: pt.x,
              y: pt.y,
              text: `<b>€${pt.y.toLocaleString()}</b>`,
              showarrow: true,
              arrowhead: 2,
              arrowcolor: '#004481',
              ax: 0,
              ay: -35,
              font: { size: 13, color: '#002e5a', family: 'Inter' },
              bgcolor: '#fff',
              bordercolor: '#c2c6d2',
              borderwidth: 1,
              borderpad: 6,
            }],
          });
          setTimeout(() => Plotly.relayout('chart-liquidity', { annotations: [] }), 3000);
        });
      }
    }, 100);
  }

  applyCrossfilter(selectedType: string | null): void {
    const chartEl = document.getElementById('chart-liquidity');
    if (!chartEl) return;

    const barCount = (chartEl as any)?.data?.[0]?.x?.length ?? 0;
    if (selectedType) {
      const muted = this.BAR_COLORS.slice(0, barCount).map(c => c + '30');
      Plotly.restyle('chart-liquidity', { 'marker.color': [muted], 'marker.opacity': [0.5] }, [0]);
    } else {
      Plotly.restyle('chart-liquidity', {
        'marker.color': [this.BAR_COLORS.slice(0, barCount)],
        'marker.opacity': [0.9],
      }, [0]);
    }
  }
}
