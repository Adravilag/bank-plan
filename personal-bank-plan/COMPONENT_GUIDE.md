# Guía: Añadir un nuevo componente gráfico

## Arquitectura actual

```
Backend (Django)                    Frontend (Angular)
─────────────────                   ──────────────────
services/analytics.py  ──►  views/analytics.py  ──►  urls.py
        │                                                │
        │                         HTTP GET /api/...      │
        │                                                ▼
        │                         bank.service.ts  ◄─────┘
        │                                │
        │                                ▼
        └─────────────────►  components/mi-grafica/
                                         │
                                         ▼
                              pages/dashboard/ (lo consume)
```

---

## Paso 1 — Backend: Función de datos

**Archivo:** `backend/dashboard/services/analytics.py`

```python
def get_mi_nueva_metrica():
    """Descripción breve de lo que calcula."""
    data = (
        MiModelo.objects
        .values('campo')
        .annotate(total=Sum('valor'), count=Count('id'))
        .order_by('campo')
    )
    return [
        {'label': d['campo'], 'value': float(d['total']), 'count': d['count']}
        for d in data
    ]
```

**Convenciones:**
- Nombre `get_` + descripción en snake_case
- Retornar tipos serializables (`float`, `str`, `int`, `list`, `dict`)
- Usar `aggregate`/`annotate` de Django ORM, no queries raw
- Docstring en español breve

---

## Paso 2 — Backend: Vista

**Archivo:** `backend/dashboard/views/analytics.py`

```python
from ..services import get_mi_nueva_metrica

@api_view(['GET'])
def mi_nueva_metrica(request):
    """Descripción del endpoint."""
    return Response(get_mi_nueva_metrica())
```

**Exportar en** `backend/dashboard/views/__init__.py`:
```python
from .analytics import mi_nueva_metrica
```

**Exportar en** `backend/dashboard/services/__init__.py`:
```python
from .analytics import get_mi_nueva_metrica
```

---

## Paso 3 — Backend: URL

**Archivo:** `backend/dashboard/urls.py`

```python
path('analytics/mi-nueva-metrica/', views.mi_nueva_metrica),
```

**Convención:** usar kebab-case en URLs.

---

## Paso 4 — Frontend: Interfaz + Servicio

**Archivo:** `frontend/src/app/services/bank.service.ts`

```typescript
// 1. Definir interfaz
export interface MiNuevaMetrica {
  label: string;
  value: number;
  count: number;
}

// 2. Agregar método en BankService
getMiNuevaMetrica(): Observable<MiNuevaMetrica[]> {
  return this.http.get<MiNuevaMetrica[]>(`${API}/analytics/mi-nueva-metrica/`);
}
```

---

## Paso 5 — Frontend: Componente

Generar con CLI:
```bash
cd frontend
npx ng generate component components/mi-nueva-grafica
```

### 5.1 — TypeScript (`mi-nueva-grafica.component.ts`)

```typescript
import { Component, OnInit, input } from '@angular/core';
import { CommonModule } from '@angular/common';
import Plotly from 'plotly.js-dist-min';

// Interfaz de datos que recibe el componente
export interface MiGraficaData {
  labels: string[];
  values: number[];
}

@Component({
  selector: 'app-mi-nueva-grafica',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './mi-nueva-grafica.component.html',
  styleUrl: './mi-nueva-grafica.component.scss',
})
export class MiNuevaGraficaComponent implements OnInit {
  // Usar input signals (no @Input)
  data = input.required<MiGraficaData>();

  ngOnInit(): void {
    const { labels, values } = this.data();
    if (!labels.length) return;

    setTimeout(() => this.renderChart(labels, values), 100);
  }

  private renderChart(labels: string[], values: number[]): void {
    Plotly.newPlot(
      'chart-mi-grafica',  // ID único, nunca repetir
      [{
        x: labels,
        y: values,
        type: 'bar',
        marker: { color: '#004481' },
        hovertemplate: '<b>%{x}</b><br>%{y:,.0f}<extra></extra>',
      }],
      {
        // Estilos consistentes con el resto del dashboard
        paper_bgcolor: 'transparent',
        plot_bgcolor: 'transparent',
        font: { family: 'Inter', color: '#424750', size: 11 },
        margin: { t: 10, b: 40, l: 70, r: 20 },
        xaxis: { gridcolor: '#f0f0f0', linecolor: '#e2e2e2' },
        yaxis: { gridcolor: '#f0f0f0', linecolor: '#e2e2e2' },
        hoverlabel: {
          bgcolor: '#fff',
          bordercolor: '#c2c6d2',
          font: { family: 'Inter', color: '#002e5a', size: 13 },
        },
      },
      { responsive: true, displayModeBar: false }
    );
  }
}
```

### 5.2 — HTML (`mi-nueva-grafica.component.html`)

```html
<section class="card">
  <div class="card-header">
    <div>
      <h3 class="card-title">Título de la Gráfica</h3>
      <p class="card-subtitle">Descripción breve</p>
    </div>
  </div>
  <div id="chart-mi-grafica" class="chart-area"></div>
</section>
```

### 5.3 — SCSS (`mi-nueva-grafica.component.scss`)

Reutilizar las clases compartidas del dashboard. Evitar estilos custom salvo que sea necesario.

---

## Paso 6 — Frontend: Integrar en Dashboard

**Archivo:** `frontend/src/app/pages/dashboard/dashboard.component.ts`

```typescript
// 1. Import
import { MiNuevaGraficaComponent, MiGraficaData } from '../../components/mi-nueva-grafica/mi-nueva-grafica.component';

// 2. Agregar al array de imports del @Component
imports: [..., MiNuevaGraficaComponent],

// 3. Signal para los datos
miGraficaData = signal<MiGraficaData | null>(null);

// 4. Cargar en ngOnInit
this.bankService.getMiNuevaMetrica().subscribe((data) => {
  this.miGraficaData.set({
    labels: data.map(d => d.label),
    values: data.map(d => d.value),
  });
});
```

**Archivo:** `frontend/src/app/pages/dashboard/dashboard.component.html`

```html
@if (miGraficaData(); as mgData) {
  <app-mi-nueva-grafica [data]="mgData" />
}
```

---

## Checklist rápido

```
□ services/analytics.py     → función get_xxx()
□ services/__init__.py       → exportar función
□ views/analytics.py         → vista @api_view
□ views/__init__.py           → exportar vista
□ dashboard/urls.py           → path(...)
□ bank.service.ts             → interfaz + método
□ components/xxx/             → componente (TS + HTML + SCSS)
□ dashboard.component.ts      → import + signal + carga
□ dashboard.component.html    → uso del componente
```

---

## Convenciones del proyecto

| Aspecto | Convención |
|---------|-----------|
| Estado Angular | Signals (`signal`, `input`, `computed`), no decoradores `@Input` |
| Componentes | `standalone: true` siempre |
| Gráficas | Plotly.js con `paper_bgcolor: 'transparent'` |
| IDs de chart | Únicos por componente, prefijo `chart-` |
| Colores | `#002e5a`, `#004481`, `#723101`, `#94a3b8`, `#1e3a5f` |
| Fuente | `Inter` |
| Backend | Lógica en `services/`, vistas delgadas en `views/` |
| URLs API | kebab-case bajo `/api/analytics/` |
| Traducciones | Mapear en el dashboard, no en el backend |
