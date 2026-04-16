# Global Ledger — The Digital Vault

Panel de gestión bancaria institucional con dashboard analítico, gestión de cuentas, transacciones y préstamos.

## Tech Stack

| Capa     | Tecnología                        |
|----------|-----------------------------------|
| Frontend | Angular 21, Plotly.js, TypeScript |
| Backend  | Django 6, Django REST Framework   |
| BD       | SQLite3                           |

## Requisitos

- **Node.js** ≥ 20 y **npm** ≥ 10
- **Python** ≥ 3.12

## Instalación

### Backend

```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data   # Genera datos de prueba
python manage.py runserver
```

El servidor arranca en `http://localhost:8000`.

### Frontend

```bash
cd frontend
npm install
npm start
```

La app arranca en `http://localhost:4200`.

## API Endpoints

### Autenticación

| Método | Endpoint            | Descripción       |
|--------|---------------------|--------------------|
| POST   | `/api/auth/login/`  | Iniciar sesión     |

### CRUD

| Recurso        | Endpoint               |
|----------------|------------------------|
| Cuentas        | `/api/accounts/`       |
| Transacciones  | `/api/transactions/`   |
| Préstamos      | `/api/loans/`          |

### Dashboard / Analíticas

| Endpoint                                  | Descripción                        |
|-------------------------------------------|------------------------------------|
| `/api/dashboard/summary/`                 | Resumen general del dashboard      |
| `/api/dashboard/transactions-by-type/`    | Transacciones agrupadas por tipo   |
| `/api/dashboard/transactions-by-month/`   | Transacciones agrupadas por mes    |
| `/api/dashboard/balance-by-account-type/` | Saldos por tipo de cuenta          |
| `/api/dashboard/loan-summary/`            | Resumen de préstamos               |
| `/api/dashboard/cash-flow/`               | Flujo de caja mensual              |
| `/api/dashboard/top-accounts/`            | Cuentas con mayor saldo            |
| `/api/dashboard/monthly-growth/`          | Crecimiento mensual                |

## Rutas del Frontend

| Ruta             | Página         | Protegida |
|------------------|----------------|-----------|
| `/login`         | Login          | No        |
| `/dashboard`     | Dashboard      | Sí        |
| `/accounts`      | Cuentas        | Sí        |
| `/transactions`  | Transacciones  | Sí        |

## Estructura del Proyecto

```
backend/
├── config/            # Configuración Django (settings, urls, wsgi)
├── dashboard/
│   ├── models/        # Account, Transaction, Loan
│   ├── serializers/   # Serializers DRF
│   ├── services/      # Lógica de analíticas
│   ├── views/         # Vistas API (auth, account, transaction, loan, analytics)
│   └── management/    # Comandos (seed_data)
frontend/
├── src/app/
│   ├── components/    # Componentes reutilizables (charts, metric-card, etc.)
│   ├── pages/         # Páginas (dashboard, accounts, transactions, login)
│   ├── services/      # AuthService, BankService
│   └── guards/        # Auth guard
```

## Datos de Prueba

```bash
python manage.py seed_data
```

Genera: 20 cuentas, 500 transacciones (últimos 12 meses) y 10 préstamos.

## Añadir un Nuevo Gráfico

Consulta [COMPONENT_GUIDE.md](COMPONENT_GUIDE.md) para el flujo completo:

`services/analytics.py → views/analytics.py → urls.py → bank.service.ts → componente → página`
