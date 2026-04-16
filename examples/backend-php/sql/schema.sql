-- Schema para PostgreSQL
-- Ejecutar: psql -U postgres -d bank_plan -f schema.sql

CREATE TABLE IF NOT EXISTS accounts (
    id            BIGSERIAL PRIMARY KEY,
    account_number VARCHAR(20) UNIQUE NOT NULL,
    holder_name    VARCHAR(200) NOT NULL,
    account_type   VARCHAR(20) NOT NULL CHECK (account_type IN ('savings','checking','credit','investment')),
    balance        NUMERIC(15,2) NOT NULL DEFAULT 0,
    created_at     TIMESTAMP NOT NULL DEFAULT NOW(),
    is_active      BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS transactions (
    id               BIGSERIAL PRIMARY KEY,
    account_id       BIGINT NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    transaction_type VARCHAR(20) NOT NULL CHECK (transaction_type IN ('deposit','withdrawal','transfer','payment','fee')),
    amount           NUMERIC(15,2) NOT NULL,
    description      VARCHAR(300) DEFAULT '',
    date             TIMESTAMP NOT NULL,
    category         VARCHAR(100) DEFAULT ''
);

CREATE TABLE IF NOT EXISTS loans (
    id                BIGSERIAL PRIMARY KEY,
    account_id        BIGINT NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    amount            NUMERIC(15,2) NOT NULL,
    interest_rate     NUMERIC(5,2) NOT NULL,
    term_months       INTEGER NOT NULL,
    monthly_payment   NUMERIC(15,2) NOT NULL,
    remaining_balance NUMERIC(15,2) NOT NULL,
    status            VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active','paid','defaulted')),
    start_date        DATE NOT NULL
);

-- Índices para consultas analíticas
CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date);
CREATE INDEX IF NOT EXISTS idx_transactions_account ON transactions(account_id);
CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(transaction_type);
CREATE INDEX IF NOT EXISTS idx_loans_status ON loans(status);
CREATE INDEX IF NOT EXISTS idx_accounts_type ON accounts(account_type);
CREATE INDEX IF NOT EXISTS idx_accounts_active ON accounts(is_active);

-- Usuario admin para login (password: admin123)
-- El hash se genera con password_hash('admin123', PASSWORD_BCRYPT)
CREATE TABLE IF NOT EXISTS users (
    id       BIGSERIAL PRIMARY KEY,
    username VARCHAR(150) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);
