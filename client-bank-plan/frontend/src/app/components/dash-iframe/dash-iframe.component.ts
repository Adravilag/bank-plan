import {
  Component,
  Input,
  Output,
  EventEmitter,
  ElementRef,
  viewChild,
  AfterViewInit,
  OnDestroy,
  OnChanges,
  SimpleChanges,
  signal,
} from '@angular/core';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';

const DASH_BASE_URL = 'http://localhost:8000/dash/';
const DASH_ORIGIN = 'http://localhost:8000';

@Component({
  selector: 'app-dash-iframe',
  standalone: true,
  template: `
    <div class="dash-wrapper">
      @if (title) {
        <div class="dash-header">
          <div>
            <h3 class="dash-title">{{ title }}</h3>
            @if (subtitle) {
              <span class="dash-subtitle">{{ subtitle }}</span>
            }
          </div>
        </div>
      }
      <div class="dash-container" [style.height]="height">
        @if (loading()) {
          <div class="dash-loading">
            <div class="loading-spinner"></div>
          </div>
        }
        <iframe
          #dashFrame
          [src]="iframeSrc"
          [style.height]="height"
          [class.loaded]="!loading()"
          frameborder="0"
          scrolling="no"
          (load)="onIframeLoad()"
        ></iframe>
      </div>
    </div>
  `,
  styles: `
    .dash-wrapper {
      background: #fff;
      border-radius: 12px;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
      overflow: hidden;
      transition: box-shadow 0.25s ease;
      opacity: 0;
      transform: translateY(24px);
      animation: fadeSlideUp 0.6s ease-out 0.3s forwards;
    }
    .dash-wrapper:hover {
      box-shadow: 0 6px 20px rgba(0, 0, 0, 0.06);
    }
    @keyframes fadeSlideUp {
      from { opacity: 0; transform: translateY(24px); }
      to { opacity: 1; transform: translateY(0); }
    }
    .dash-header {
      padding: 20px 24px 0;
      display: flex;
      align-items: baseline;
      justify-content: space-between;
      gap: 12px;
    }
    .dash-title {
      font-size: 15px;
      font-weight: 700;
      color: #1e3a5f;
      margin: 0;
      letter-spacing: -0.3px;
    }
    .dash-subtitle {
      font-size: 11px;
      color: #94a3b8;
      font-weight: 500;
      margin-top: 4px;
      display: block;
    }
    .dash-container {
      width: 100%;
      position: relative;
    }
    .dash-loading {
      position: absolute;
      inset: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      background: #fff;
      z-index: 1;
    }
    .loading-spinner {
      width: 28px;
      height: 28px;
      border: 3px solid #f1f5f9;
      border-top-color: #004481;
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
    }
    @keyframes spin { to { transform: rotate(360deg); } }
    iframe {
      width: 100%;
      border: none;
      opacity: 0;
      transition: opacity 0.3s ease;
    }
    iframe.loaded {
      opacity: 1;
    }
  `,
})
export class DashIframeComponent implements AfterViewInit, OnDestroy, OnChanges {
  @Input() chart: string = 'cash-flow';
  @Input() height: string = '400px';
  @Input() title: string = '';
  @Input() subtitle: string = '';
  @Input() filter: Record<string, unknown> | null = null;
  @Output() crossfilter = new EventEmitter<{ source: string; label: string | null }>();

  dashFrame = viewChild<ElementRef<HTMLIFrameElement>>('dashFrame');
  iframeSrc: SafeResourceUrl;
  loading = signal(true);

  private messageHandler: ((event: MessageEvent) => void) | null = null;

  constructor(private sanitizer: DomSanitizer) {
    this.iframeSrc = this.buildSrc('cash-flow');
  }

  ngAfterViewInit(): void {
    this.messageHandler = (event: MessageEvent) => {
      if (event.origin !== DASH_ORIGIN) return;
      const data = event.data;
      if (data?.type === 'crossfilter') {
        this.crossfilter.emit({
          source: data.source,
          label: data.payload?.label ?? null,
        });
      }
    };
    window.addEventListener('message', this.messageHandler);
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['chart']) {
      this.loading.set(true);
      this.iframeSrc = this.buildSrc(this.chart);
    }
    if (changes['filter'] && this.filter) {
      this.sendFilter(this.filter);
    }
  }

  onIframeLoad(): void {
    this.loading.set(false);
  }

  sendMessage(type: string, payload: unknown): void {
    const frame = this.dashFrame()?.nativeElement;
    if (frame?.contentWindow) {
      frame.contentWindow.postMessage({ type, payload }, DASH_ORIGIN);
    }
  }

  sendFilter(payload: Record<string, unknown>): void {
    this.sendMessage('dash-filter', payload);
  }

  sendCrossfilter(label: string | null): void {
    this.sendMessage('crossfilter', { label });
  }

  ngOnDestroy(): void {
    if (this.messageHandler) {
      window.removeEventListener('message', this.messageHandler);
    }
  }

  private buildSrc(chart: string): SafeResourceUrl {
    return this.sanitizer.bypassSecurityTrustResourceUrl(
      `${DASH_BASE_URL}?chart=${encodeURIComponent(chart)}`
    );
  }
}
