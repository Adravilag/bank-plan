import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Component } from '@angular/core';
import { LiquidityForecastComponent, LiquidityData } from './liquidity-forecast.component';

const { mockPlotly } = vi.hoisted(() => ({
  mockPlotly: {
    newPlot: vi.fn().mockResolvedValue(undefined),
    animate: vi.fn().mockResolvedValue(undefined),
    restyle: vi.fn().mockResolvedValue(undefined),
    relayout: vi.fn().mockResolvedValue(undefined),
  },
}));

vi.mock('plotly.js-dist-min', () => ({ default: mockPlotly }));

const MOCK_DATA: LiquidityData = {
  labels: ['Ahorro', 'Corriente', 'Crédito', 'Inversión'],
  values: [500000, 300000, 150000, 200000],
  counts: [20, 15, 10, 5],
  avgs: [25000, 20000, 15000, 40000],
  maxes: [80000, 60000, 30000, 100000],
};

@Component({
  standalone: true,
  imports: [LiquidityForecastComponent],
  template: `<app-liquidity-forecast [data]="data" />`,
})
class TestHostComponent {
  data: LiquidityData = MOCK_DATA;
}

describe('LiquidityForecastComponent', () => {
  let fixture: ComponentFixture<TestHostComponent>;
  let el: HTMLElement;

  beforeEach(async () => {
    mockPlotly.newPlot.mockClear();
    mockPlotly.animate.mockClear();
    mockPlotly.restyle.mockClear();

    await TestBed.configureTestingModule({
      imports: [TestHostComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(TestHostComponent);
    fixture.autoDetectChanges(true);
    el = fixture.nativeElement;
  });

  it('should create', () => {
    expect(el.querySelector('app-liquidity-forecast')).toBeTruthy();
  });

  it('should render title', () => {
    expect(el.querySelector('.card-title')?.textContent).toContain('Liquidity Forecast');
  });

  it('should render subtitle', () => {
    expect(el.querySelector('.card-subtitle')?.textContent).toContain('Balance por tipo de cuenta');
  });

  it('should render chart container', () => {
    expect(el.querySelector('#chart-liquidity')).toBeTruthy();
  });

  it('should apply crossfilter without crashing when no DOM element', () => {
    const comp = fixture.debugElement.children[0].componentInstance as LiquidityForecastComponent;
    expect(() => comp.applyCrossfilter('Depósito')).not.toThrow();
  });

  it('should restore colors without crashing on crossfilter null', () => {
    const comp = fixture.debugElement.children[0].componentInstance as LiquidityForecastComponent;
    comp.applyCrossfilter('Depósito');
    expect(() => comp.applyCrossfilter(null)).not.toThrow();
  });

  it('should not crash with empty data', async () => {
    fixture.componentInstance.data = { labels: [], values: [], counts: [], avgs: [], maxes: [] };
    fixture.detectChanges();
    expect(el.querySelector('#chart-liquidity')).toBeTruthy();
  });
});
