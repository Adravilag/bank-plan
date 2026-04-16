import { Component, input, effect } from '@angular/core';
import { CommonModule } from '@angular/common';
import Plotly from 'plotly.js-dist-min';

@Component({
  selector: 'app-metric-card',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './metric-card.component.html',
  styleUrl: './metric-card.component.scss',
})
export class MetricCardComponent {
  label = input.required<string>();
  value = input.required<string>();
  badgeText = input<string>('');
  badgeType = input<'positive' | 'neutral' | 'info'>('neutral');
  accentColor = input<'blue' | 'orange' | 'teal'>('blue');
  sparklineId = input<string>('');
  sparklineColor = input<string>('#004481');
  sparklineData = input<number[]>([]);
  subtitle = input<string>('');
  trendValue = input<string>('');
  trendDirection = input<'up' | 'down' | 'none'>('none');
  trendLabel = input<string>('');

  gaugeValue = input<number | null>(null);
  gaugeLabel = input<string>('');

  constructor() {
    effect(() => {
      const data = this.sparklineData();
      const id = this.sparklineId();
      const color = this.sparklineColor();
      if (data.length && id) {
        setTimeout(() => this.renderSparkline(id, data, color), 50);
      }
    });
  }

  private renderSparkline(elementId: string, values: number[], color: string): void {
    const el = document.getElementById(elementId);
    if (!el) return;

    Plotly.newPlot(
      elementId,
      [{
        y: values,
        type: 'scatter',
        mode: 'lines',
        fill: 'tozeroy',
        line: { color, width: 1.5, shape: 'spline' },
        fillcolor: color + '15',
        hoverinfo: 'none',
      }],
      {
        paper_bgcolor: 'transparent',
        plot_bgcolor: 'transparent',
        margin: { t: 0, b: 0, l: 0, r: 0 },
        xaxis: { visible: false, fixedrange: true },
        yaxis: { visible: false, fixedrange: true },
        showlegend: false,
      },
      { responsive: true, displayModeBar: false, staticPlot: true }
    );
  }
}
