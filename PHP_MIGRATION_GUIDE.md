# Guía de Migración: PHP Legacy → Django + Angular

Documentación para migrar un sistema bancario legacy PHP (con PostgreSQL) al stack moderno Django 6 + Angular 21.

---

## 1. Comparativa de Stacks

| Aspecto          | PHP Legacy (backend-php/)        | Django + Angular (actual)                |
|------------------|----------------------------------|------------------------------------------|
| Backend          | PHP puro, procedural             | Django 6 + Django REST Framework         |
| Frontend         | PHP templates / HTML             | Angular 21 SPA (TypeScript)              |
| Base de datos    | PostgreSQL (SQL directo via PDO) | PostgreSQL (Django ORM)                  |
| ORM              | Ninguno — queries manuales       | Django ORM (models, querysets, migrations)|
| Auth             | bcrypt + password_verify manual  | django.contrib.auth + tokens             |
| Routing          | Router manual en index.php       | urls.py + DefaultRouter DRF              |
| Serialización    | json_encode manual               | DRF Serializers (validación automática)  |
| CORS             | Headers manuales                 | django-cors-headers                      |
| Migraciones DB   | SQL scripts manuales             | Django migrations (versionadas)          |
| Seed data        | Script PHP (seed.php)            | Management command (seed_data.py)        |
| Tests            | Ninguno                          | Vitest (frontend) + Django TestCase      |

---

## 2. Mapeo de Archivos: PHP → Django

### Configuración

| PHP Legacy                    | Django                          |
|-------------------------------|---------------------------------|
| `config/database.php`        | `config/settings.py` (DATABASES)|
| `config/helpers.php`         | No necesario (DRF lo maneja)    |
| `sql/schema.sql`             | `dashboard/migrations/`         |
| `index.php` (router)         | `config/urls.py` + `dashboard/urls.py` |

### Controladores → Views

| PHP Legacy                         | Django                              |
|------------------------------------|-------------------------------------|
| `controllers/accounts.php`        | `dashboard/views/account.py`       |
| `controllers/transactions.php`    | `dashboard/views/transaction.py`   |
| `controllers/loans.php`           | `dashboard/views/loan.py`          |
| `controllers/analytics.php`       | `dashboard/views/analytics.py` + `dashboard/services/analytics.py` |
| `controllers/auth.php`            | `dashboard/views/auth.py`          |

### SQL manual → Django ORM

| PHP Legacy                         | Django                              |
|------------------------------------|-------------------------------------|
| `CREATE TABLE accounts ...`        | `dashboard/models/account.py`      |
| `CREATE TABLE transactions ...`    | `dashboard/models/transaction.py`  |
| `CREATE TABLE loans ...`           | `dashboard/models/loan.py`         |
| `SELECT ... GROUP BY` en analytics | `dashboard/services/analytics.py` (ORM aggregation) |

---

## 3. Migración de Modelos

### PHP: Schema SQL manual

```sql
-- backend-php/sql/schema.sql
CREATE TABLE accounts (
    id             BIGSERIAL PRIMARY KEY,
    account_number VARCHAR(20) UNIQUE NOT NULL,
    holder_name    VARCHAR(200) NOT NULL,
    account_type   VARCHAR(20) NOT NULL,
    balance        NUMERIC(15,2) DEFAULT 0,
    created_at     TIMESTAMP DEFAULT NOW(),
    is_active      BOOLEAN DEFAULT TRUE
);
```

### Django: Modelo ORM equivalente

```python
# dashboard/models/account.py
class Account(models.Model):
    ACCOUNT_TYPES = [
        ('savings', 'Cuenta de Ahorro'),
        ('checking', 'Cuenta Corriente'),
        ('credit', 'Tarjeta de Crédito'),
        ('investment', 'Inversión'),
    ]
    account_number = models.CharField(max_length=20, unique=True)
    holder_name    = models.CharField(max_length=200)
    account_type   = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    balance        = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    created_at     = models.DateTimeField(auto_now_add=True)
    is_active      = models.BooleanField(default=True)
```

**Ventajas del ORM**:
- Migraciones versionadas (`python manage.py makemigrations` / `migrate`)
- Validación de `choices` automática
- No hay riesgo de SQL inconsistente entre schema y código
- Las relaciones FK se definen con `ForeignKey` en vez de SQL manual

---

## 4. Migración de Queries

### PHP: SQL directo con PDO

```php
// controllers/analytics.php — Dashboard summary
$row = $db->query("
    SELECT
        (SELECT COUNT(*) FROM accounts) AS total_accounts,
        (SELECT COALESCE(SUM(balance), 0) FROM accounts) AS total_balance,
        (SELECT COUNT(*) FROM transactions) AS total_transactions,
        (SELECT COUNT(*) FROM loans WHERE status = 'active') AS active_loans,
        (SELECT COALESCE(SUM(remaining_balance), 0) FROM loans WHERE status = 'active') AS total_loan_amount
")->fetch();
json_response($row);
```

### Django: ORM con aggregation

```python
# dashboard/services/analytics.py
def get_dashboard_summary():
    total_accounts = Account.objects.count()
    active_accounts = Account.objects.filter(is_active=True).count()
    total_balance = Account.objects.aggregate(total=Sum('balance'))['total'] or 0
    total_transactions = Transaction.objects.count()
    active_loans = Loan.objects.filter(status='active').count()
    total_loan_amount = Loan.objects.filter(status='active').aggregate(
        total=Sum('remaining_balance')
    )['total'] or 0

    return {
        'total_accounts': total_accounts,
        'active_accounts': active_accounts,
        'total_balance': float(total_balance),
        'total_transactions': total_transactions,
        'active_loans': active_loans,
        'total_loan_amount': float(total_loan_amount),
    }
```

### PHP: Cash flow con CASE/WHEN SQL

```php
$rows = $db->query("
    SELECT TO_CHAR(DATE_TRUNC('month', date), 'YYYY-MM') AS month,
           SUM(CASE WHEN transaction_type = 'deposit' THEN amount ELSE 0 END) AS deposits,
           SUM(CASE WHEN transaction_type = 'withdrawal' THEN amount ELSE 0 END) AS withdrawals
    FROM transactions
    GROUP BY DATE_TRUNC('month', date)
    ORDER BY DATE_TRUNC('month', date)
")->fetchAll();
```

### Django: ORM equivalente

```python
months = (
    Transaction.objects.annotate(month=TruncMonth('date'))
    .values('month')
    .annotate(
        deposits=Sum(Case(When(transaction_type='deposit', then=F('amount')),
                          default=Value(0), output_field=DecimalField())),
        withdrawals=Sum(Case(When(transaction_type='withdrawal', then=F('amount')),
                             default=Value(0), output_field=DecimalField())),
    )
    .order_by('month')
)
```

---

## 5. Migración de CRUD

### PHP: Controlador procedural manual

```php
// 90+ líneas por recurso: parsear método, query, respuesta, manejo de errores
function handle_accounts(array $segments): void {
    $method = request_method();
    $id = $segments[1] ?? null;
    if ($id === null && $method === 'GET') {
        $stmt = $db->query('SELECT * FROM accounts ORDER BY id');
        json_response($stmt->fetchAll());
    }
    // ... PUT, PATCH, DELETE, POST ...
}
```

### Django: ModelViewSet (5 líneas)

```python
# dashboard/views/account.py
class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
```

```python
# dashboard/urls.py
router = DefaultRouter()
router.register(r'accounts', AccountViewSet)
```

DRF genera automáticamente: list, create, retrieve, update, partial_update, destroy.

---

## 6. Migración de Auth

### PHP Legacy

```php
$stmt = $db->prepare('SELECT * FROM users WHERE username = :username');
$stmt->execute(['username' => $username]);
$user = $stmt->fetch();

if (!$user || !password_verify($password, $user['password'])) {
    json_response(['error' => 'Credenciales inválidas'], 401);
}

$token = hash('sha256', random_bytes(32));
```

### Django

```python
from django.contrib.auth import authenticate

user = authenticate(username=username, password=password)
if user is None:
    return Response({'error': 'Credenciales inválidas'}, status=401)

token = hashlib.sha256(secrets.token_hex(32).encode()).hexdigest()
```

**Ventaja Django**: `django.contrib.auth` maneja hashing, salting, y la tabla de usuarios automáticamente. No necesitas crear la tabla `users` manualmente.

---

## 7. Migración de Base de Datos (PostgreSQL → Django)

### Opción A: Migrar datos existentes (recomendado)

```bash
# 1. Crear modelos Django y generar migraciones
python manage.py makemigrations

# 2. Configurar Django para usar la misma PostgreSQL
# config/settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'bank_plan',
        'USER': 'postgres',
        'PASSWORD': 'tu_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# 3. Fake la migración inicial (las tablas ya existen)
python manage.py migrate --fake-initial

# 4. Renombrar tablas si es necesario
# PHP usa: accounts, transactions, loans
# Django usa: dashboard_account, dashboard_transaction, dashboard_loan
```

### Opción B: Migración limpia

```bash
# 1. Exportar datos de PostgreSQL
pg_dump -U postgres -d bank_plan --data-only -t accounts -t transactions -t loans > data_dump.sql

# 2. Crear BD Django desde cero
python manage.py migrate

# 3. Adaptar e importar datos (ajustar nombres de tablas)
sed -i 's/accounts/dashboard_account/g' data_dump.sql
sed -i 's/transactions/dashboard_transaction/g' data_dump.sql
sed -i 's/loans/dashboard_loan/g' data_dump.sql
psql -U postgres -d bank_plan_django -f data_dump.sql

# 4. Crear superusuario
python manage.py createsuperuser
```

### Opción C: Mantener nombres de tabla PHP

En los modelos Django, usar `db_table` para evitar renombrar:

```python
class Account(models.Model):
    # ... campos ...
    class Meta:
        db_table = 'accounts'  # Usa la tabla PHP tal cual
```

### Mapeo de tablas

| PHP (PostgreSQL)  | Django por defecto            | Django con db_table  |
|-------------------|-------------------------------|----------------------|
| `accounts`        | `dashboard_account`           | `accounts`           |
| `transactions`    | `dashboard_transaction`       | `transactions`       |
| `loans`           | `dashboard_loan`              | `loans`              |
| `users`           | `auth_user` (Django built-in) | —                    |

---

## 8. Frontend: de PHP Templates a Angular SPA

| Aspecto         | PHP Legacy                           | Angular 21                               |
|-----------------|--------------------------------------|------------------------------------------|
| Renderizado     | Server-side (echo/include)           | Client-side SPA                          |
| Navegación      | Cada URL = nueva página PHP          | Router SPA (sin recargas)                |
| Estado          | Sesiones PHP ($_SESSION)             | Signals + localStorage                   |
| HTTP calls      | No aplica (todo server-side)         | HttpClient → REST API                    |
| Templates       | PHP mezclado con HTML                | Angular templates (.html) separados      |
| Estilos         | CSS/SCSS globales                    | SCSS por componente (encapsulados)       |
| Gráficos        | Librerías JS insertadas              | Plotly.js con angular-plotly.js          |
| Auth guard      | Verificación en cada .php            | Route guard (authGuard)                  |

### Arquitectura resultante

```
┌──────────────┐     HTTP/JSON     ┌──────────────────┐
│   Angular    │ ◄──────────────► │   Django + DRF    │
│   (SPA)      │   localhost:4200  │   localhost:8000   │
│              │                   │                    │
│ Components   │                   │ Views/ViewSets     │
│ Services     │ ──── GET/POST ──► │ Serializers        │
│ Guards       │ ◄── JSON ──────── │ Services           │
│ Routes       │                   │ Models (ORM)       │
└──────────────┘                   └────────┬───────────┘
                                            │
                                   ┌────────▼───────────┐
                                   │    PostgreSQL       │
                                   └────────────────────┘
```

---

## 9. Checklist de Migración

### Fase 1 — Infraestructura

- [ ] Instalar Python 3.12+, Node.js 20+
- [ ] Crear proyecto Django (`django-admin startproject config`)
- [ ] Crear app dashboard (`python manage.py startapp dashboard`)
- [ ] Instalar dependencias: `django`, `djangorestframework`, `django-cors-headers`
- [ ] Configurar Django para conectar a la PostgreSQL existente
- [ ] Crear proyecto Angular (`ng new frontend`)

### Fase 2 — Modelos y datos

- [ ] Crear modelos Django equivalentes a las tablas PHP
- [ ] Generar migraciones (`makemigrations`)
- [ ] Migrar datos existentes (ver Sección 7)
- [ ] Crear serializers DRF para cada modelo
- [ ] Crear management command para seed data

### Fase 3 — API REST

- [ ] Crear ViewSets CRUD (Account, Transaction, Loan)
- [ ] Registrar en router DRF
- [ ] Verificar paridad de endpoints con PHP
- [ ] Migrar lógica de analytics SQL a services/analytics.py
- [ ] Crear views para los 8 endpoints analíticos
- [ ] Implementar auth login endpoint

### Fase 4 — Frontend Angular

- [ ] Crear componentes equivalentes a las vistas/páginas PHP
- [ ] Crear servicios (BankService, AuthService)
- [ ] Implementar routing con guards
- [ ] Integrar Plotly.js para gráficos del dashboard
- [ ] Conectar formularios a la API REST

### Fase 5 — Validación y cutover

- [ ] Comparar respuestas JSON de PHP vs Django endpoint por endpoint
- [ ] Verificar que los gráficos muestran los mismos datos
- [ ] Test de rendimiento (queries analíticas)
- [ ] Configurar CORS para producción
- [ ] Apuntar el dominio al nuevo stack
- [ ] Mantener PHP en modo read-only como fallback temporal

---

## 10. Riesgos y Consideraciones

| Riesgo | Mitigación |
|--------|------------|
| Pérdida de datos durante migración | Hacer backup completo de PostgreSQL antes de empezar |
| Diferencias en formato JSON | Comparar respuesta a respuesta con tests automáticos |
| Queries analíticas con resultados distintos | Verificar que Django ORM genera el mismo SQL que las queries manuales |
| Nombres de tablas diferentes | Usar `db_table` en Meta de los modelos Django |
| Tipos de datos Decimal | Django usa Python Decimal; verificar que no se pierda precisión |
| Auth incompatible | Los hashes bcrypt de PHP son compatibles con Django (ver Sección 11) |
| Downtime durante cutover | Estrategia blue-green: correr ambos backends en paralelo temporalmente |

---

## 11. Compatibilidad de Hashes de Passwords

Si los usuarios de PHP usan `password_hash()` con `PASSWORD_BCRYPT`, Django puede verificarlos añadiendo en settings:

```python
# config/settings.py
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
]
```

Instalar: `pip install bcrypt`

Esto permite que los usuarios existentes sigan logueándose sin resetear contraseñas.
