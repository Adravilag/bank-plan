import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Component } from '@angular/core';
import { MetricCardComponent } from './metric-card.component';

const { mockPlotly } = vi.hoisted(() => ({
  mockPlotly: { newPlot: vi.fn().mockResolvedValue(undefined) },
}));

vi.mock('plotly.js-dist-min', () => ({ default: mockPlotly }));

@Component({
  standalone: true,
  imports: [MetricCardComponent],
  template: `
    <app-metric-card
      [label]="label"
      [value]="value"
      [badgeText]="badgeText"
      [badgeType]="badgeType"
      [accentColor]="accentColor"
      [subtitle]="subtitle"
      [trendValue]="trendValue"
      [trendDirection]="trendDirection"
      [trendLabel]="trendLabel"
      [gaugeValue]="gaugeValue"
      [gaugeLabel]="gaugeLabel"
      [sparklineId]="sparklineId"
      [sparklineData]="sparklineData"
    />
  `,
})
class TestHostComponent {
  label = 'Operating Balance';
  value = '$100,000.00';
  badgeText = 'Active';
  badgeType: 'positive' | 'neutral' | 'info' = 'positive';
  accentColor: 'blue' | 'orange' | 'teal' = 'blue';
  subtitle = '';
  trendValue = '$5,000.00';
  trendDirection: 'up' | 'down' | 'none' = 'up';
  trendLabel = 'vs mes anterior';
  gaugeValue: number | null = null;
  gaugeLabel = '';
  sparklineId = '';
  sparklineData: number[] = [];
}

describe('MetricCardComponent', () => {
  let fixture: ComponentFixture<TestHostComponent>;
  let host: TestHostComponent;
  let el: HTMLElement;

  async function createComponent(overrides: Partial<TestHostComponent> = {}) {
    await TestBed.configureTestingModule({
      imports: [TestHostComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(TestHostComponent);
    host = fixture.componentInstance;
    Object.assign(host, overrides);
    fixture.detectChanges();
    el = fixture.nativeElement;
  }

  it('should create', async () => {
    await createComponent();
    expect(el.querySelector('app-metric-card')).toBeTruthy();
  });

  it('should display label and value', async () => {
    await createComponent();
    expect(el.querySelector('.metric-label')?.textContent).toContain('Operating Balance');
    expect(el.querySelector('.metric-value')?.textContent).toContain('$100,000.00');
  });

  it('should show badge with correct class', async () => {
    await createComponent();
    const badge = el.querySelector('.metric-badge');
    expect(badge?.textContent).toContain('Active');
    expect(badge?.classList.contains('badge-positive')).toBe(true);
  });

  it('should hide badge when badgeText is empty', async () => {
    await createComponent({ badgeText: '' });
    expect(el.querySelector('.metric-badge')).toBeNull();
  });

  it('should show upward trend', async () => {
    await createComponent();
    expect(el.querySelector('.trend-up')?.textContent).toContain('+$5,000.00');
    expect(el.querySelector('.metric-sub')?.textContent).toContain('vs mes anterior');
  });

  it('should show downward trend', async () => {
    await createComponent({ trendDirection: 'down', trendValue: '$2,000.00' });
    expect(el.querySelector('.trend-down')?.textContent).toContain('$2,000.00');
  });

  it('should hide trend when direction is none', async () => {
    await createComponent({ trendDirection: 'none' });
    expect(el.querySelector('.metric-trend')).toBeNull();
  });

  it('should display subtitle', async () => {
    await createComponent({ trendDirection: 'none', subtitle: 'Across 50 accounts' });
    expect(el.querySelector('.metric-sub')?.textContent).toContain('Across 50 accounts');
  });

  it('should show gauge when gaugeValue is provided', async () => {
    await createComponent({ gaugeValue: 75, gaugeLabel: '75% utilización' });
    const fill = el.querySelector('.gauge-fill') as HTMLElement;
    expect(fill).toBeTruthy();
    expect(fill.style.width).toBe('75%');
    expect(el.querySelector('.gauge-label')?.textContent).toContain('75% utilización');
  });

  it('should hide gauge when gaugeValue is null', async () => {
    await createComponent({ gaugeValue: null });
    expect(el.querySelector('.loan-gauge')).toBeNull();
  });

  it('should apply correct accent color class', async () => {
    await createComponent({ accentColor: 'orange' });
    expect(el.querySelector('.accent-orange')).toBeTruthy();
  });

  it('should render sparkline container when sparklineId is set', async () => {
    await createComponent({ sparklineId: 'spark-test' });
    expect(el.querySelector('#spark-test')).toBeTruthy();
  });

  it('should not render sparkline container when sparklineId is empty', async () => {
    await createComponent({ sparklineId: '' });
    expect(el.querySelector('.sparkline')).toBeNull();
  });
});
