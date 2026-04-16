# Client Bank Plan

Panel de gestión bancaria para clientes con dashboard analítico en tiempo real, gestión de cuentas, transacciones y préstamos.

## Tech Stack

| Capa       | Tecnología                                      |
|------------|--------------------------------------------------|
| Frontend   | Angular 21, TypeScript, Socket.IO Client         |
| Backend    | Flask 3, Flask-SocketIO, SQLAlchemy              |
| Charts     | Dash 3 (micro-frontend), Plotly, Bootstrap       |
| BD         | SQLite3                                          |
| Tiempo real| WebSockets (Socket.IO / eventlet)                |

## Requisitos

- **Python** ≥ 3.12
- **Node.js** ≥ 20 y **npm** ≥ 10

## Instalación

### 1. Entorno virtual (desde la raíz del workspace)

```bash
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows
```

### 2. Backend

```bash
cd backend
pip install -r requirements.txt
python seed.py          # Genera datos de prueba (10 cuentas, transacciones, 6 préstamos)
python app.py           # Arranca en http://localhost:8000
```

### 3. Frontend

```bash
cd frontend
npm install
npm start               # Arranca en http://localhost:4200
```

## Credenciales de prueba

| Usuario | Contraseña |
|---------|------------|
| `admin` | `admin123` |

## API Endpoints

### Autenticación

| Método | Endpoint           | Descripción    |
|--------|--------------------|----------------|
| POST   | `/api/auth/login/` | Iniciar sesión |

### CRUD

| Recurso       | Endpoint             | Operaciones                    |
|---------------|----------------------|--------------------------------|
| Cuentas       | `/api/accounts/`     | GET, POST, PUT, PATCH, DELETE  |
| Transacciones | `/api/transactions/` | GET, POST, PUT, PATCH, DELETE  |
| Préstamos     | `/api/loans/`        | GET, POST, PUT, PATCH, DELETE  |

### Dashboard / Analíticas

| Endpoint                                  | Descripción                      |
|-------------------------------------------|----------------------------------|
| `/api/dashboard/summary/`                 | Resumen general del dashboard    |
| `/api/dashboard/transactions-by-type/`    | Transacciones agrupadas por tipo |
| `/api/dashboard/transactions-by-month/`   | Transacciones agrupadas por mes  |
| `/api/dashboard/balance-by-account-type/` | Saldos por tipo de cuenta        |
| `/api/dashboard/loan-summary/`            | Resumen de préstamos             |
| `/api/dashboard/cash-flow/`               | Flujo de caja mensual            |
| `/api/dashboard/top-accounts/`            | Cuentas con mayor saldo          |
| `/api/dashboard/monthly-growth/`          | Crecimiento mensual              |

### Dash (Charts)

Los gráficos se sirven como micro-frontend en `/dash/` y se integran vía `<iframe>`:

| URL                                  | Gráfico                   |
|--------------------------------------|---------------------------|
| `/dash/?chart=cash-flow`             | Flujo de caja             |
| `/dash/?chart=expense-distribution`  | Distribución de gastos    |
| `/dash/?chart=liquidity-forecast`    | Previsión de liquidez     |
| `/dash/?chart=loan-summary`          | Resumen de préstamos      |

### WebSocket (namespace `/dashboard`)

| Evento               | Dirección | Descripción                             |
|----------------------|-----------|-----------------------------------------|
| `connect`            | servidor  | Emite `dashboard_update` con resumen    |
| `request_update`     | cliente   | Solicita datos actualizados             |
| `transaction_created`| servidor  | Se emite al crear una transacción       |

## Rutas del Frontend

| Ruta             | Página        | Protegida |
|------------------|---------------|-----------|
| `/login`         | Login         | No        |
| `/dashboard`     | Dashboard     | Sí        |
| `/accounts`      | Cuentas       | Sí        |
| `/transactions`  | Transacciones | Sí        |

## Estructura del Proyecto

```
backend/
├── app.py                 # Entry point (Flask + SocketIO)
├── seed.py                # Generador de datos de prueba
├── config/                # Configuración Flask (settings, urls)
├── dashboard/
│   ├── models/            # Account, Transaction, Loan
│   ├── serializers/       # Serialización JSON
│   ├── services/          # Lógica de analíticas
│   └── views/             # Vistas API (auth, account, transaction, loan, analytics)
├── dash_app/
│   ├── __init__.py        # Factory del Dash app
│   ├── theme.py           # Colores, fuentes, CSS compartido
│   ├── charts.py          # Builders de figuras Plotly
│   ├── layouts.py         # Layouts de cada gráfico
│   ├── callbacks.py       # Callbacks server-side y clientside
│   └── assets/
│       └── clientside.js  # JavaScript para callbacks clientside
frontend/
├── src/app/
│   ├── components/        # Componentes reutilizables (metric-card, charts)
│   ├── pages/             # Páginas (dashboard, accounts, transactions, login)
│   ├── services/          # AuthService, BankService, SocketService
│   └── guards/            # Auth guard
```

## Scripts disponibles (Frontend)

| Comando         | Descripción                |
|-----------------|----------------------------|
| `npm start`     | Servidor de desarrollo     |
| `npm run build` | Build de producción        |
| `npm run watch` | Build con watch            |
| `npm test`      | Tests (Vitest)             |
