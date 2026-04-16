# Personal Bank Plan

Panel de gestión bancaria personal con dashboard analítico, gestión de cuentas, transacciones y préstamos.

## Tech Stack

| Capa     | Tecnología                        |
|----------|-----------------------------------|
| Frontend | Angular 21, Plotly.js, TypeScript |
| Backend  | Django 6, Django REST Framework   |
| Alt. Backend | PHP 8 (sin framework)        |
| BD       | SQLite3 (Django) / PostgreSQL (PHP) |

## Requisitos

- **Python** ≥ 3.12
- **Node.js** ≥ 20 y **npm** ≥ 10
- **PHP** ≥ 8.1 y **PostgreSQL** ≥ 14 (solo para el backend PHP)

## Instalación

### 1. Entorno virtual (desde la raíz del workspace)

```bash
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows
```

### 2. Backend (Django)

```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data   # Genera datos de prueba (20 cuentas, 500 transacciones, 10 préstamos)
python manage.py runserver   # Arranca en http://localhost:8000
```

### 3. Backend alternativo (PHP)

```bash
cd backend-php
# Crear la base de datos PostgreSQL
psql -U postgres -c "CREATE DATABASE bank_plan;"
psql -U postgres -d bank_plan -f sql/schema.sql
php seed.php               # Genera datos de prueba
php -S localhost:8000 index.php
```

### 4. Frontend

```bash
cd frontend
npm install
npm start                  # Arranca en http://localhost:4200
```

El frontend funciona con cualquiera de los dos backends.

## Credenciales de prueba

| Usuario | Contraseña |
|---------|------------|
| `admin` | `admin123` |

## API Endpoints

### Autenticación

| Método | Endpoint            | Descripción    |
|--------|---------------------|----------------|
| POST   | `/api/auth/login/`  | Iniciar sesión |

### CRUD

| Recurso       | Endpoint             | Operaciones                    |
|---------------|----------------------|--------------------------------|
| Cuentas       | `/api/accounts/`     | GET, POST, PUT, PATCH, DELETE  |
| Transacciones | `/api/transactions/` | GET, POST, PUT, PATCH, DELETE  |
| Préstamos     | `/api/loans/`        | GET, POST, PUT, PATCH, DELETE  |

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
backend-php/
├── index.php          # Router principal
├── seed.php           # Generador de datos de prueba
├── config/            # Conexión BD y helpers
├── controllers/       # Controladores (accounts, transactions, loans, auth, analytics)
└── sql/               # Schema SQL
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

## Scripts disponibles (Frontend)

| Comando         | Descripción                |
|-----------------|----------------------------|
| `npm start`     | Servidor de desarrollo     |
| `npm run build` | Build de producción        |
| `npm run watch` | Build con watch            |
| `npm test`      | Tests (Vitest)             |
