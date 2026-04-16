import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Component } from '@angular/core';
import { ExpenseDistributionComponent } from './expense-distribution.component';

const { mockPlotly } = vi.hoisted(() => ({
  mockPlotly: {
    newPlot: vi.fn().mockResolvedValue(undefined),
    animate: vi.fn().mockResolvedValue(undefined),
    restyle: vi.fn().mockResolvedValue(undefined),
  },
}));

vi.mock('plotly.js-dist-min', () => ({ default: mockPlotly }));

const MOCK_DATA = {
  labels: ['Depósito', 'Retiro', 'Transferencia', 'Pago', 'Comisión'],
  values: [50, 30, 10, 7, 3],
};

@Component({
  standalone: true,
  imports: [ExpenseDistributionComponent],
  template: `
    <app-expense-distribution
      [data]="data"
      [totalTransactions]="100"
      (filterChanged)="lastFilter = $event"
    />
  `,
})
class TestHostComponent {
  data = MOCK_DATA;
  lastFilter: string | null = null;
}

describe('ExpenseDistributionComponent', () => {
  let fixture: ComponentFixture<TestHostComponent>;
  let host: TestHostComponent;
  let el: HTMLElement;

  beforeEach(async () => {
    mockPlotly.newPlot.mockClear();
    mockPlotly.animate.mockClear();
    mockPlotly.restyle.mockClear();

    await TestBed.configureTestingModule({
      imports: [TestHostComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(TestHostComponent);
    host = fixture.componentInstance;
    fixture.autoDetectChanges(true);
    el = fixture.nativeElement;
  });

  it('should create', () => {
    expect(el.querySelector('app-expense-distribution')).toBeTruthy();
  });

  it('should render title', () => {
    expect(el.querySelector('.card-title')?.textContent).toContain('Expense Distribution');
  });

  it('should render legend items for each category', () => {
    const legendItems = el.querySelectorAll('.legend-item');
    expect(legendItems.length).toBe(5);
  });

  it('should display correct labels in legend', () => {
    const texts = Array.from(el.querySelectorAll('.legend-text')).map(e => e.textContent?.trim());
    expect(texts).toContain('Depósito');
    expect(texts).toContain('Retiro');
    expect(texts).toContain('Transferencia');
  });

  it('should display correct values in legend', () => {
    const vals = Array.from(el.querySelectorAll('.legend-val')).map(e => e.textContent?.trim());
    expect(vals).toContain('50');
    expect(vals).toContain('30');
  });

  it('should display percentages in legend', () => {
    const pcts = Array.from(el.querySelectorAll('.legend-pct')).map(e => e.textContent?.trim());
    expect(pcts).toContain('50.0%');
    expect(pcts).toContain('30.0%');
  });

  it('should show total transactions in donut center by default', () => {
    expect(el.querySelector('.donut-pct')?.textContent).toContain('100');
    expect(el.querySelector('.donut-name')?.textContent).toContain('Transacciones');
  });

  it('should render donut chart container', () => {
    expect(el.querySelector('#chart-expense')).toBeTruthy();
  });

  it('should emit filterChanged on legend click', () => {
    const comp = fixture.debugElement.children[0].componentInstance as ExpenseDistributionComponent;
    comp.onExpenseClick(0);
    fixture.detectChanges();
    expect(host.lastFilter).toBe('Depósito');
  });

  it('should deselect on second click of same item', () => {
    const comp = fixture.debugElement.children[0].componentInstance as ExpenseDistributionComponent;
    comp.onExpenseClick(0);
    comp.onExpenseClick(0);
    fixture.detectChanges();
    expect(host.lastFilter).toBeNull();
  });

  it('should apply legend-active class on selection', () => {
    const comp = fixture.debugElement.children[0].componentInstance as ExpenseDistributionComponent;
    comp.onExpenseClick(1);
    fixture.detectChanges();
    const items = el.querySelectorAll('.legend-item');
    expect(items[1].classList.contains('legend-active')).toBe(true);
    expect(items[0].classList.contains('legend-dimmed')).toBe(true);
  });

  it('should not show filter badge when no filter active', () => {
    expect(el.querySelector('.filter-badge')).toBeNull();
  });

  it('should show filter badge when filter is active', () => {
    const comp = fixture.debugElement.children[0].componentInstance as ExpenseDistributionComponent;
    comp.onExpenseClick(0);
    fixture.detectChanges();
    const badge = el.querySelector('.filter-badge');
    expect(badge).toBeTruthy();
    expect(badge?.textContent).toContain('Depósito');
  });

  it('should reset filter on badge click', () => {
    const comp = fixture.debugElement.children[0].componentInstance as ExpenseDistributionComponent;
    comp.onExpenseClick(0);
    fixture.detectChanges();
    comp.resetFilter();
    fixture.detectChanges();
    expect(el.querySelector('.filter-badge')).toBeNull();
    expect(host.lastFilter).toBeNull();
  });

  it('should not crash with empty data', async () => {
    host.data = { labels: [], values: [] };
    fixture.detectChanges();
    expect(el.querySelector('#chart-expense')).toBeTruthy();
  });
});
