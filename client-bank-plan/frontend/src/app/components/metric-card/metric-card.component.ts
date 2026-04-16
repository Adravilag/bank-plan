import { Component, input, AfterViewInit, ElementRef, viewChild } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-metric-card',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './metric-card.component.html',
  styleUrl: './metric-card.component.scss',
})
export class MetricCardComponent implements AfterViewInit {
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

  private sparklineEl = viewChild<ElementRef>('sparklineRef');

  gaugeValue = input<number | null>(null);
  gaugeLabel = input<string>('');

  sparklinePath = '';

  ngAfterViewInit(): void {
    const data = this.sparklineData();
    if (data.length) {
      setTimeout(() => this.buildSparklinePath(data), 50);
    }
  }

  private buildSparklinePath(values: number[]): void {
    if (!values.length) return;
    const width = 200;
    const height = 40;
    const max = Math.max(...values);
    const min = Math.min(...values);
    const range = max - min || 1;
    const step = width / (values.length - 1);

    const points = values.map((v, i) => {
      const x = i * step;
      const y = height - ((v - min) / range) * height;
      return `${x},${y}`;
    });

    this.sparklinePath = `M${points.join(' L')}`;
  }
}
