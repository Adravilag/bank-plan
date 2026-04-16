# Guía de Arquitectura: Flask + Dash + Angular (Iframe)

Documentación del stack propuesto por el cliente para el dashboard bancario.

---

## 1. Visión General

```
Angular 21 SPA (:4200)                    Flask + Dash (:8000)
─────────────────────                      ──────────────────────
                                           
  ┌─────────────────┐   HTTP/JSON          ┌──────────────────┐
  │  pages/          │ ◄───────────────►   │  routes/         │ ── REST API
  │  dashboard/      │                     │  (accounts,      │
  │                  │   WebSocket          │   transactions,  │
  │  services/       │ ◄───────────────►   │   loans, auth,   │
  │  websocket.ts    │   /dashboard ns     │   analytics)     │
  │                  │                     └──────┬───────────┘
  │  components/     │                            │
  │  dash-iframe/    │   ← iframe src →    ┌──────▼───────────┐
  │  ┌─────────────┐ │   /dash/?chart=X    │  dash_app/       │
  │  │  <iframe>   │─┼───────────────────► │  (theme, charts, │
  │  │  Dash app   │ │   postMessage ↕     │   layouts,       │
  │  └─────────────┘ │   crossfilter       │   callbacks)     │
  └─────────────────┘                     └──────┬───────────┘
                                                  │
                                           ┌──────▼───────────┐
                                           │  SQLite / ORM    │
                                           │  (SQLAlchemy)    │
                                           └──────────────────┘
```

### Principios de diseño

| Principio | Implementación |
|-----------|---------------|
| **Micro-frontend** | Dash como aplicación embebida vía iframe, no integrada en el bundle Angular |
| **Separación de responsabilidades** | Angular = layout + navegación + estado; Dash = visualización + interactividad de gráficos |
| **Comunicación desacoplada** | `postMessage` entre iframe↔Angular, WebSocket para push en tiempo real |
| **Charts server-rendered** | Plotly genera los gráficos en el servidor (Dash), Angular no necesita `plotly.js` |
| **Tipografía consistente** | Google Fonts (Inter) cargado tanto en Angular como en Dash vía CDN |

---

## 2. Estructura de Archivos

```
client-bank-plan/
├── backend/
│   ├── app.py                    ← Flask factory (create_app)
│   ├── config.py                 ← SECRET_KEY, SQLALCHEMY_DATABASE_URI, CORS
│   ├── extensions.py             ← db = SQLAlchemy(), socketio = SocketIO()
│   ├── seed.py                   ← Generador de datos demo
│   ├── websocket_events.py       ← Eventos Socket.IO (/dashboard)
│   ├── requirements.txt
│   ├── models/
│   │   ├── __init__.py           ← Exporta Account, Transaction, Loan
│   │   ├── account.py
│   │   ├── transaction.py
│   │   └── loan.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── accounts.py           ← CRUD /api/accounts/
│   │   ├── transactions.py       ← CRUD /api/transactions/
│   │   ├── loans.py              ← CRUD /api/loans/
│   │   ├── auth.py               ← POST /api/auth/login/
│   │   └── analytics.py          ← GET /api/dashboard/*
│   ├── services/
│   │   ├── __init__.py
│   │   └── analytics.py          ← Funciones de agregación (SQLAlchemy)
│   └── dash_app/
│       ├── __init__.py            ← Dash factory (create_dash_app)
│       ├── theme.py               ← Colores, tipografía, CSS dicts
│       ├── charts.py              ← Constructores de figuras Plotly
│       ├── layouts.py             ← Wrappers (figura + controles)
│       └── callbacks.py           ← Callbacks server-side y clientside
└── frontend/
    └── src/app/
        ├── app.config.ts          ← provideRouter, provideHttpClient
        ├── app.routes.ts          ← /login, /dashboard, /accounts, /transactions
        ├── guards/
        │   └── auth.guard.ts      ← canActivate: token en localStorage
        ├── services/
        │   ├── auth.service.ts    ← Login, logout, token, signal isAuthenticated
        │   ├── bank.service.ts    ← 10+ métodos HTTP contra /api/*
        │   └── websocket.service.ts ← Socket.IO client con signals
        ├── components/
        │   ├── dash-iframe/       ← Wrapper de iframe para Dash charts
        │   └── metric-card/       ← KPI card con sparklines SVG
        └── pages/
            ├── dashboard/         ← Orquestador: métricas + iframes + ledger
            ├── accounts/
            ├── transactions/
            └── login/
```

---

## 3. Flujo de Datos

### 3.1 Carga inicial del dashboard

```
1. Angular  → GET /api/dashboard/summary/         → BankService.getSummary()
2. Angular  → GET /api/accounts/?limit=5           → BankService.getAccounts()
3. Angular  → GET /api/dashboard/top-accounts/     → BankService.getTopAccounts()
4. Angular  → GET /api/dashboard/loan-summary/     → BankService.getLoanSummary()
5. Angular  → GET /api/dashboard/transactions-by-month/ → sparkline data
6. Angular  → WebSocket connect /dashboard         → Recibe summary inicial
7. <iframe> → GET /dash/?chart=cash-flow           → Dash renderiza el gráfico
8. <iframe> → GET /dash/?chart=expense-distribution
9. <iframe> → GET /dash/?chart=liquidity-forecast
```

### 3.2 Crossfilter (interacción entre gráficos)

```
Usuario hace click en un slice del donut (expense-distribution)
    │
    ▼
Dash callback: on_expense_click()
    → Actualiza figura con slice seleccionado
    → Clientside JS: window.parent.postMessage({type:'crossfilter', ...})
        │
        ▼
    Angular DashIframeComponent: window.addEventListener('message')
        → Emite @Output crossfilter event
            │
            ▼
        DashboardComponent.onCrossfilter(event)
            → Llama liquidityChart.sendCrossfilter(label)
                → postMessage al iframe de liquidity
                    │
                    ▼
                Dash clientside callback: window.addEventListener('message')
                    → Plotly.restyle() para atenuar barras no relacionadas
```

### 3.3 WebSocket (tiempo real)

```
POST /api/transactions/  (nueva transacción creada)
    │
    ▼
Flask route emite → socketio.emit('transaction_created', data, namespace='/dashboard')
    │
    ▼
Angular WebSocketService → signal transactionCreated.set(data)
    → Dashboard puede recargar datos automáticamente
```

---

## 4. Comparativa con el Proyecto Personal

| Aspecto | personal-bank-plan | client-bank-plan |
|---------|-------------------|------------------|
| **Backend** | Django 6 + DRF | Flask 3 + Blueprints |
| **Gráficos** | Angular + plotly.js (client-side) | Dash + Plotly (server-side, iframe) |
| **Bundle JS** | ~2MB (incluye plotly.js) | ~1.4MB (sin plotly.js) |
| **Interactividad** | Plotly.js directo en el DOM | Dash callbacks (server + clientside JS) |
| **Tiempo real** | No | WebSocket (Socket.IO) |
| **ORM** | Django ORM | SQLAlchemy |
| **BD** | PostgreSQL | SQLite (demo) |
| **CRUD** | DRF ViewSets (5 líneas) | Flask Blueprints (manual) |
| **Auth** | django.contrib.auth | Demo in-memory (admin/admin123) |
| **Tipografía** | Inter (local) | Inter (Google Fonts CDN) |
| **Crossfilter** | Signals entre componentes | postMessage entre iframes |

---

## 5. Añadir un Nuevo Gráfico

### Paso 1 — Backend: función de datos

**Archivo:** `backend/services/analytics.py`

```python
def get_mi_nueva_metrica():
    """Descripción breve de lo que calcula."""
    from models import Transaction
    from sqlalchemy import func

    data = (
        db.session.query(
            Transaction.category,
            func.sum(Transaction.amount).label('total'),
            func.count(Transaction.id).label('count'),
        )
        .group_by(Transaction.category)
        .order_by(func.sum(Transaction.amount).desc())
        .all()
    )
    return [
        {'label': row.category, 'value': float(row.total), 'count': row.count}
        for row in data
    ]
```

**Exportar en** `backend/services/__init__.py`:
```python
from .analytics import get_mi_nueva_metrica
```

### Paso 2 — Backend: endpoint REST (opcional)

Si Angular necesita los datos crudos (no solo el gráfico Dash):

**Archivo:** `backend/routes/analytics.py`

```python
@analytics_bp.route('/dashboard/mi-nueva-metrica/')
def mi_nueva_metrica():
    return jsonify(get_mi_nueva_metrica())
```

### Paso 3 — Dash: constructor de figura

**Archivo:** `backend/dash_app/charts.py`

```python
from services.analytics import get_mi_nueva_metrica
from .theme import PRIMARY, SLATE_500, HOVERLABEL

def build_mi_nueva_grafica() -> go.Figure:
    """Descripción del gráfico."""
    data = get_mi_nueva_metrica()
    if not data:
        return apply_common_layout(go.Figure())

    fig = go.Figure(data=[go.Bar(
        x=[d['label'] for d in data],
        y=[d['value'] for d in data],
        marker=dict(color=PRIMARY),
        hovertemplate='<b>%{x}</b><br>€%{y:,.0f}<extra></extra>',
    )])

    fig.update_layout(
        margin=dict(t=30, b=40, l=70, r=20),
        hoverlabel=HOVERLABEL, dragmode=False,
    )
    return apply_common_layout(fig)
```

### Paso 4 — Dash: layout wrapper

**Archivo:** `backend/dash_app/layouts.py`

```python
from .charts import build_mi_nueva_grafica

def layout_mi_nueva_grafica():
    """Layout sin controles extra."""
    fig = build_mi_nueva_grafica()

    children = html.Div([
        dcc.Graph(
            id='mi-nueva-graph', figure=fig,
            config={'responsive': True, 'displayModeBar': False},
            style=_CHART_STYLE,
        ),
    ], style=_WRAPPER_STYLE)

    return children, {}
```

### Paso 5 — Dash: registrar ruta

**Archivo:** `backend/dash_app/callbacks.py`

Dentro de `register_callbacks()`, en el callback `render_chart`:

```python
builders = {
    'cash-flow': layout_cash_flow,
    'expense-distribution': layout_expense_distribution,
    'liquidity-forecast': layout_liquidity_forecast,
    'loan-summary': layout_loan_summary,
    'mi-nueva-grafica': layout_mi_nueva_grafica,    # ← Añadir
}
```

Importar en la cabecera:
```python
from .layouts import ..., layout_mi_nueva_grafica
```

### Paso 6 — Angular: usar el iframe

**Archivo:** `frontend/src/app/pages/dashboard/dashboard.component.html`

```html
<app-dash-iframe
  chart="mi-nueva-grafica"
  title="Mi Nueva Gráfica"
  subtitle="Descripción breve"
  height="300px"
/>
```

No se necesitan cambios en `BankService` ni instalar `plotly.js`.

### Checklist rápido

```
□ services/analytics.py       → función get_xxx()
□ services/__init__.py         → exportar función
□ dash_app/charts.py           → build_xxx() con apply_common_layout
□ dash_app/layouts.py          → layout_xxx() con Graph + controles
□ dash_app/callbacks.py        → añadir al dict builders en render_chart
□ dashboard.component.html     → <app-dash-iframe chart="xxx" />
```

---

## 6. Añadir Interactividad a un Gráfico

### 6.1 Animación de entrada

En el layout, añadir un `dcc.Interval` que dispare una sola vez:

```python
dcc.Interval(id='mi-grafica-anim', interval=500, max_intervals=1),
```

En callbacks, registrar un clientside callback:

```python
dash_app.clientside_callback(
    """
    function(n) {
        if (!n) return window.dash_clientside.no_update;
        var g = document.querySelector('#mi-nueva-graph .js-plotly-plot');
        if (!g || !g.data) return window.dash_clientside.no_update;
        var realY = g.data[0].y.slice();
        Plotly.restyle(g, {y: [realY.map(function(){return 0})]}, [0]);
        setTimeout(function() {
            Plotly.animate(g, {
                data: [{y: realY}], traces: [0], layout: {}
            }, {transition: {duration: 1000, easing: 'cubic-in-out'},
                frame: {duration: 1000, redraw: true}});
        }, 300);
        return window.dash_clientside.no_update;
    }
    """,
    Output('_dummy-mi-grafica-anim', 'data'),
    Input('mi-grafica-anim', 'n_intervals'),
    prevent_initial_call=True,
)
```

Añadir el store dummy en `__init__.py`:
```python
dcc.Store(id='_dummy-mi-grafica-anim', data=None),
```

### 6.2 Hover dimming

```javascript
// En un clientside callback:
g.on('plotly_hover', function(e) {
    var idx = e.points[0].pointNumber;
    var dimmed = colors.map(function(c, i) {
        return i === idx ? c : c + '30';
    });
    Plotly.restyle(g, {'marker.color': [dimmed]}, [0]);
});
g.on('plotly_unhover', function() {
    Plotly.restyle(g, {'marker.color': [colors]}, [0]);
});
```

### 6.3 Crossfilter (comunicación entre charts)

**Emisor (Dash → Angular):**
```javascript
g.on('plotly_click', function(e) {
    var label = e.points[0].label;
    window.parent.postMessage({
        type: 'crossfilter',
        source: 'mi-chart',
        payload: { label: label }
    }, 'http://localhost:4200');
});
```

**Receptor (Angular → Dash):**
```javascript
window.addEventListener('message', function(event) {
    if (event.origin !== 'http://localhost:4200') return;
    if (event.data && event.data.type === 'crossfilter') {
        // Atenuar/resaltar barras según event.data.payload.label
    }
});
```

**Angular (conectar dos iframes):**
```typescript
// En dashboard.component.ts:
@ViewChild('emisorChart') emisorChart!: DashIframeComponent;
@ViewChild('receptorChart') receptorChart!: DashIframeComponent;

onCrossfilter(event: { source: string; label: string | null }) {
  this.receptorChart.sendCrossfilter(event.label);
}
```

```html
<!-- En dashboard.component.html -->
<app-dash-iframe #emisorChart chart="emisor" (crossfilter)="onCrossfilter($event)" />
<app-dash-iframe #receptorChart chart="receptor" />
```

---

## 7. Dash App: Estructura de Módulos

```
dash_app/
├── __init__.py    ← Factory: create_dash_app(flask_app)
│                     • Crea Dash app con Bootstrap + Google Fonts
│                     • Define layout raíz (stores, intervals, container)
│                     • Llama register_callbacks()
│
├── theme.py       ← Design tokens (no imports de Dash ni Plotly)
│                     • ANGULAR_ORIGIN
│                     • Paleta: PRIMARY, PRIMARY_CONTAINER, BLUE_900, SLATE_*
│                     • EXPENSE_COLORS, BAR_COLORS
│                     • FONT_FAMILY, GOOGLE_FONTS_URL
│                     • CSS dicts: TOGGLE_*, FILTER_BADGE, HOVERLABEL
│
├── charts.py      ← Funciones puras: datos → go.Figure
│                     • apply_common_layout(fig)
│                     • build_cash_flow(months_slice)
│                     • build_expense_distribution(selected_index)
│                     • build_liquidity_forecast(muted)
│                     • build_loan_summary()
│
├── layouts.py     ← Figura + controles Dash → (html.Div, store_data)
│                     • layout_cash_flow()        → toggles + graph + interval
│                     • layout_expense_distribution() → graph + reset + badge
│                     • layout_liquidity_forecast()   → graph + interval
│                     • layout_loan_summary()         → graph
│
└── callbacks.py   ← Todos los callbacks registrados
                      • register_callbacks(dash_app, flask_app)
                      • PostMessage listener (clientside)
                      • render_chart: ?chart=X → layout_*()
                      • update_cashflow_range: toggles 12M/6M/3M
                      • on_expense_click: selección + crossfilter
                      • 4× clientside: animaciones, hover, crossfilter
```

### Reglas de dependencia

```
theme.py ← No importa nada del proyecto
charts.py ← Importa theme.py + services/analytics.py
layouts.py ← Importa theme.py + charts.py
callbacks.py ← Importa theme.py + charts.py + layouts.py
__init__.py ← Importa theme.py + callbacks.py
```

---

## 8. API REST — Endpoints

### CRUD

| Método | URL | Descripción |
|--------|-----|-------------|
| GET | `/api/accounts/` | Listar cuentas |
| GET | `/api/accounts/<id>/` | Detalle cuenta |
| POST | `/api/accounts/` | Crear cuenta |
| PUT | `/api/accounts/<id>/` | Actualizar completa |
| PATCH | `/api/accounts/<id>/` | Actualizar parcial |
| DELETE | `/api/accounts/<id>/` | Eliminar |
| GET | `/api/transactions/` | Listar (filtro `?account=`) |
| POST | `/api/transactions/` | Crear (emite WebSocket) |
| GET | `/api/loans/` | Listar préstamos |
| POST | `/api/auth/login/` | Login demo (admin/admin123) |

### Analytics

| URL | Retorna |
|-----|---------|
| `/api/dashboard/summary/` | KPIs globales |
| `/api/dashboard/transactions-by-type/` | Agrupado por tipo |
| `/api/dashboard/transactions-by-month/` | Serie temporal |
| `/api/dashboard/balance-by-account-type/` | Balance por tipo de cuenta |
| `/api/dashboard/loan-summary/` | Agrupado por estado |
| `/api/dashboard/cash-flow/` | Depósitos/retiros/neto por mes |
| `/api/dashboard/top-accounts/?limit=N` | Top cuentas por balance |
| `/api/dashboard/monthly-growth/` | Cambio mes a mes |

---

## 9. Convenciones del Proyecto

| Aspecto | Convención |
|---------|-----------|
| **Estado Angular** | Signals (`signal`, `input`, `computed`), no `@Input` decoradores |
| **Componentes** | `standalone: true` siempre |
| **Gráficos** | Dash + Plotly server-side, embebido vía iframe — Angular NO importa plotly.js |
| **IDs de Graph** | Únicos por chart, sin prefijo `chart-` (ej: `cashflow-graph`, `expense-graph`) |
| **Colores** | `#002e5a` (primary), `#004481` (container), `#1e3a5f`, `#94a3b8`, `#64748b` |
| **Fuente** | Inter (Google Fonts CDN), weights 300–700 |
| **Backend** | Lógica de negocio en `services/`, rutas delgadas en `routes/` |
| **Dash** | Figuras en `charts.py`, layouts en `layouts.py`, callbacks en `callbacks.py` |
| **URLs API** | kebab-case bajo `/api/` |
| **postMessage** | Siempre validar `event.origin` contra `ANGULAR_ORIGIN` |
| **Callbacks clientside** | Outputs a `dcc.Store` dummy (`_dummy-*`), retornar `no_update` |
| **Animaciones** | `dcc.Interval` con `max_intervals=1` + `Plotly.animate()` |
| **Crossfilter** | `postMessage` tipo `crossfilter` con `{source, payload: {label}}` |
| **WebSocket** | Namespace `/dashboard`, signals en Angular para estado reactivo |
| **Traducciones** | Labels mapeados en Dash (`charts.py`), no en el backend |

---

## 10. Comandos de Desarrollo

```bash
# Backend
cd client-bank-plan/backend
python -m venv ../../venv
source ../../venv/bin/activate          # Linux/Mac
../../venv/Scripts/Activate.ps1          # Windows PowerShell
pip install -r requirements.txt
python seed.py                           # Crear datos demo
python app.py                            # Servidor en :8000

# Frontend
cd client-bank-plan/frontend
npm install
npx ng serve                             # Dev server en :4200
npx ng build                             # Build de producción
```

---

## 11. Riesgos y Consideraciones

| Riesgo | Mitigación |
|--------|------------|
| Latencia del iframe (carga Dash + Plotly) | Spinner de carga + animación de entrada post-render |
| Seguridad postMessage | Validar `event.origin` en ambos lados |
| Doble carga de Bootstrap (Angular + Dash) | Dash usa su propia instancia aislada en el iframe |
| SQLite no escala | Migrar a PostgreSQL en producción (cambiar `SQLALCHEMY_DATABASE_URI`) |
| Auth demo insegura | Reemplazar por JWT o OAuth en producción |
| Eventlet deprecado | Migrar a `gevent` o `asyncio` cuando sea necesario |
| Callbacks clientside usan DOM queries | Los IDs de Dash son estables; `querySelector` funciona dentro del iframe |
| Bundle Plotly (~3MB) cargado por iframe | Se cachea en el navegador; solo afecta primera carga |
