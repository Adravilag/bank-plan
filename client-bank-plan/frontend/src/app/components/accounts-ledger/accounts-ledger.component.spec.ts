import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Component } from '@angular/core';
import { AccountsLedgerComponent } from './accounts-ledger.component';
import { Account, TopAccount } from '../../services/bank.service';

const MOCK_ACCOUNTS: Account[] = [
  { id: 1, account_number: 'ACC-001', holder_name: 'Alice Corp', account_type: 'savings', balance: 150000, is_active: true, created_at: '2024-01-01' },
  { id: 2, account_number: 'ACC-002', holder_name: 'Bob Inc', account_type: 'checking', balance: 50000, is_active: true, created_at: '2024-02-01' },
  { id: 3, account_number: 'ACC-003', holder_name: 'Charlie LLC', account_type: 'credit', balance: 80000, is_active: false, created_at: '2024-03-01' },
];

const MOCK_TOP_ACCOUNTS: TopAccount[] = [
  { id: 1, account_number: 'ACC-001', holder_name: 'Alice Corp', account_type: 'savings', balance: 150000, transaction_count: 245, total_deposited: 500000 },
  { id: 2, account_number: 'ACC-002', holder_name: 'Bob Inc', account_type: 'checking', balance: 50000, transaction_count: 120, total_deposited: 200000 },
];

@Component({
  standalone: true,
  imports: [AccountsLedgerComponent],
  template: `<app-accounts-ledger [accounts]="accounts" [topAccounts]="topAccounts" />`,
})
class TestHostComponent {
  accounts: Account[] = MOCK_ACCOUNTS;
  topAccounts: TopAccount[] = MOCK_TOP_ACCOUNTS;
}

describe('AccountsLedgerComponent', () => {
  let fixture: ComponentFixture<TestHostComponent>;
  let el: HTMLElement;
  let comp: AccountsLedgerComponent;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TestHostComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(TestHostComponent);
    fixture.autoDetectChanges(true);
    el = fixture.nativeElement;
    comp = fixture.debugElement.children[0].componentInstance;
  });

  it('should create', () => {
    expect(el.querySelector('app-accounts-ledger')).toBeTruthy();
  });

  it('should render title and subtitle', () => {
    expect(el.querySelector('.card-title')?.textContent).toContain('Contributing Accounts Ledger');
    expect(el.querySelector('.card-subtitle')?.textContent).toContain('high-impact treasury');
  });

  it('should render correct number of table rows', () => {
    const rows = el.querySelectorAll('tbody tr');
    expect(rows.length).toBe(3);
  });

  it('should display holder names', () => {
    const names = Array.from(el.querySelectorAll('.entity-name')).map(e => e.textContent?.trim());
    expect(names).toContain('Alice Corp');
    expect(names).toContain('Bob Inc');
    expect(names).toContain('Charlie LLC');
  });

  it('should display account numbers', () => {
    const monos = Array.from(el.querySelectorAll('td.mono'));
    const numbers = monos.filter((_, i) => i % 2 === 0).map(e => e.textContent?.trim());
    expect(numbers).toContain('ACC-001');
    expect(numbers).toContain('ACC-002');
  });

  it('should format currency correctly', () => {
    expect(comp.formatCurrency(150000)).toBe('150.000,00\u00a0\u20ac');
    expect(comp.formatCurrency(0)).toBe('0,00\u00a0\u20ac');
  });

  it('should translate account types', () => {
    expect(comp.getAccountTypeLabel('savings')).toBe('Ahorro');
    expect(comp.getAccountTypeLabel('checking')).toBe('Corriente');
    expect(comp.getAccountTypeLabel('credit')).toBe('Crédito');
    expect(comp.getAccountTypeLabel('investment')).toBe('Inversión');
    expect(comp.getAccountTypeLabel('unknown')).toBe('unknown');
  });

  it('should return correct status class', () => {
    expect(comp.getStatusClass(MOCK_ACCOUNTS[0])).toBe('status-liquid');
    expect(comp.getStatusClass(MOCK_ACCOUNTS[1])).toBe('status-stable');
    expect(comp.getStatusClass(MOCK_ACCOUNTS[2])).toBe('status-audit');
  });

  it('should return correct status label', () => {
    expect(comp.getStatusLabel(MOCK_ACCOUNTS[0])).toBe('Liquid');
    expect(comp.getStatusLabel(MOCK_ACCOUNTS[1])).toBe('Stable');
    expect(comp.getStatusLabel(MOCK_ACCOUNTS[2])).toBe('Auditing');
  });

  it('should calculate balance bar width proportionally', () => {
    const width = comp.getBalanceBarWidth(150000);
    expect(width).toBe(100);
    const halfWidth = comp.getBalanceBarWidth(75000);
    expect(halfWidth).toBe(50);
  });

  it('should return 0 bar width for zero balance', () => {
    expect(comp.getBalanceBarWidth(0)).toBe(0);
  });

  it('should display transaction count from topAccounts', () => {
    expect(comp.getTopAccountTxns(1)).toBe('245');
    expect(comp.getTopAccountTxns(2)).toBe('120');
  });

  it('should return dash for accounts not in topAccounts', () => {
    expect(comp.getTopAccountTxns(3)).toBe('—');
  });

  it('should render type badges', () => {
    const badges = Array.from(el.querySelectorAll('.type-badge')).map(e => e.textContent?.trim());
    expect(badges).toContain('Ahorro');
    expect(badges).toContain('Corriente');
    expect(badges).toContain('Crédito');
  });

  it('should render status pills with correct classes', () => {
    const pills = el.querySelectorAll('.status-pill');
    expect(pills[0].classList.contains('status-liquid')).toBe(true);
    expect(pills[1].classList.contains('status-stable')).toBe(true);
    expect(pills[2].classList.contains('status-audit')).toBe(true);
  });

  it('should handle zero balance gracefully', () => {
    expect(comp.getBalanceBarWidth(0)).toBe(0);
    expect(comp.formatCurrency(0)).toBe('0,00\u00a0\u20ac');
  });
});
