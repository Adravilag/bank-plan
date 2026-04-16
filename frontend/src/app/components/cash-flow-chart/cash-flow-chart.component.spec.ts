import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Component } from '@angular/core';
import { CashFlowChartComponent, CashFlowData } from './cash-flow-chart.component';

const { mockPlotly } = vi.hoisted(() => ({
  mockPlotly: {
    newPlot: vi.fn().mockResolvedValue(undefined),
    animate: vi.fn().mockResolvedValue(undefined),
    relayout: vi.fn().mockResolvedValue(undefined),
  },
}));

vi.mock('plotly.js-dist-min', () => ({ default: mockPlotly }));

const MOCK_DATA: CashFlowData = {
  months: ['2025-01', '2025-02', '2025-03', '2025-04', '2025-05', '2025-06',
           '2025-07', '2025-08', '2025-09', '2025-10', '2025-11', '2025-12'],
  totals: [1000, 2000, -500, 3000, 1500, -200, 800, 2500, 1200, -100, 3500, 2000],
  counts: [10, 15, 8, 20, 12, 5, 9, 18, 14, 6, 22, 16],
};

@Component({
  standalone: true,
  imports: [CashFlowChartComponent],
  template: `<app-cash-flow-chart [data]="data" />`,
})
class TestHostComponent {
  data: CashFlowData = MOCK_DATA;
}

describe('CashFlowChartComponent', () => {
  let fixture: ComponentFixture<TestHostComponent>;
  let el: HTMLElement;

  beforeEach(async () => {
    mockPlotly.newPlot.mockClear();
    mockPlotly.animate.mockClear();

    await TestBed.configureTestingModule({
      imports: [TestHostComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(TestHostComponent);
    fixture.autoDetectChanges(true);
    el = fixture.nativeElement;
  });

  it('should create', () => {
    expect(el.querySelector('app-cash-flow-chart')).toBeTruthy();
  });

  it('should render card with title', () => {
    expect(el.querySelector('.card-title')?.textContent).toContain('Cash Flow Trend');
  });

  it('should render subtitle', () => {
    expect(el.querySelector('.card-subtitle')?.textContent).toContain('Zoom, pan');
  });

  it('should render toggle buttons', () => {
    const buttons = el.querySelectorAll('.toggle-btn');
    expect(buttons.length).toBe(3);
    expect(buttons[0].textContent).toContain('12M');
    expect(buttons[1].textContent).toContain('6M');
    expect(buttons[2].textContent).toContain('3M');
  });

  it('should have 12M active by default', () => {
    const activeBtn = el.querySelector('.toggle-btn.active');
    expect(activeBtn?.textContent).toContain('12M');
  });

  it('should render chart container', () => {
    expect(el.querySelector('#chart-cashflow')).toBeTruthy();
  });

  it('should switch active toggle on click', () => {
    const buttons = el.querySelectorAll('.toggle-btn');
    (buttons[1] as HTMLButtonElement).click();
    fixture.detectChanges();
    expect(el.querySelector('.toggle-btn.active')?.textContent).toContain('6M');
  });

  it('should call Plotly.animate on toggle view change', () => {
    // Give ngOnInit time to process
    const comp = fixture.debugElement.children[0].componentInstance as CashFlowChartComponent;
    comp.toggleView('6M');
    expect(mockPlotly.animate).toHaveBeenCalled();
  });

  it('should not crash with empty data', async () => {
    fixture.componentInstance.data = { months: [], totals: [], counts: [] };
    fixture.detectChanges();
    expect(el.querySelector('#chart-cashflow')).toBeTruthy();
  });
});
