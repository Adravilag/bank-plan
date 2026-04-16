<?php
/**
 * Endpoints analíticos del dashboard.
 * Todas las queries usan SQL puro con PostgreSQL.
 */

require_once __DIR__ . '/../config/database.php';
require_once __DIR__ . '/../config/helpers.php';

/**
 * GET /api/dashboard/summary/
 */
function handle_dashboard_summary(): void
{
    $db = get_db();

    $row = $db->query("
        SELECT
            (SELECT COUNT(*) FROM accounts) AS total_accounts,
            (SELECT COUNT(*) FROM accounts WHERE is_active = TRUE) AS active_accounts,
            (SELECT COALESCE(SUM(balance), 0) FROM accounts) AS total_balance,
            (SELECT COUNT(*) FROM transactions) AS total_transactions,
            (SELECT COUNT(*) FROM loans WHERE status = 'active') AS active_loans,
            (SELECT COUNT(*) FROM loans) AS total_loans,
            (SELECT COALESCE(SUM(remaining_balance), 0) FROM loans WHERE status = 'active') AS total_loan_amount
    ")->fetch();

    json_response($row);
}

/**
 * GET /api/dashboard/transactions-by-type/
 */
function handle_transactions_by_type(): void
{
    $db = get_db();
    $rows = $db->query("
        SELECT transaction_type,
               COUNT(*) AS count,
               SUM(amount) AS total
        FROM transactions
        GROUP BY transaction_type
        ORDER BY transaction_type
    ")->fetchAll();

    json_response($rows);
}

/**
 * GET /api/dashboard/transactions-by-month/
 */
function handle_transactions_by_month(): void
{
    $db = get_db();
    $rows = $db->query("
        SELECT TO_CHAR(DATE_TRUNC('month', date), 'YYYY-MM') AS month,
               COUNT(*) AS count,
               SUM(amount) AS total
        FROM transactions
        GROUP BY DATE_TRUNC('month', date)
        ORDER BY DATE_TRUNC('month', date)
    ")->fetchAll();

    json_response($rows);
}

/**
 * GET /api/dashboard/balance-by-account-type/
 */
function handle_balance_by_account_type(): void
{
    $db = get_db();
    $rows = $db->query("
        SELECT account_type,
               SUM(balance) AS total_balance,
               COUNT(*) AS count,
               AVG(balance) AS avg_balance,
               MAX(balance) AS max_balance,
               MIN(balance) AS min_balance
        FROM accounts
        GROUP BY account_type
        ORDER BY account_type
    ")->fetchAll();

    json_response($rows);
}

/**
 * GET /api/dashboard/loan-summary/
 */
function handle_loan_summary(): void
{
    $db = get_db();
    $rows = $db->query("
        SELECT status,
               COUNT(*) AS count,
               SUM(amount) AS total,
               AVG(interest_rate) AS avg_rate,
               SUM(remaining_balance) AS total_remaining
        FROM loans
        GROUP BY status
        ORDER BY status
    ")->fetchAll();

    json_response($rows);
}

/**
 * GET /api/dashboard/cash-flow/
 */
function handle_cash_flow(): void
{
    $db = get_db();
    $rows = $db->query("
        SELECT TO_CHAR(DATE_TRUNC('month', date), 'YYYY-MM') AS month,
               SUM(CASE WHEN transaction_type = 'deposit'    THEN amount ELSE 0 END) AS deposits,
               SUM(CASE WHEN transaction_type = 'withdrawal' THEN amount ELSE 0 END) AS withdrawals,
               SUM(CASE WHEN transaction_type = 'transfer'   THEN amount ELSE 0 END) AS transfers,
               SUM(CASE WHEN transaction_type = 'payment'    THEN amount ELSE 0 END) AS payments,
               SUM(amount) AS total,
               COUNT(*) AS count
        FROM transactions
        GROUP BY DATE_TRUNC('month', date)
        ORDER BY DATE_TRUNC('month', date)
    ")->fetchAll();

    // Calcular net_flow y growth_pct
    $results = [];
    $prev_total = null;

    foreach ($rows as $row) {
        $total = (float)$row['total'];
        $growth = null;
        if ($prev_total !== null && $prev_total != 0) {
            $growth = round((($total - $prev_total) / $prev_total) * 100, 2);
        }

        $results[] = [
            'month'       => $row['month'],
            'deposits'    => (float)$row['deposits'],
            'withdrawals' => (float)$row['withdrawals'],
            'transfers'   => (float)$row['transfers'],
            'payments'    => (float)$row['payments'],
            'net_flow'    => (float)$row['deposits'] - (float)$row['withdrawals'],
            'total'       => $total,
            'count'       => (int)$row['count'],
            'growth_pct'  => $growth,
        ];
        $prev_total = $total;
    }

    json_response($results);
}

/**
 * GET /api/dashboard/top-accounts/?limit=N
 */
function handle_top_accounts(): void
{
    $limit = min((int)($_GET['limit'] ?? 10), 50);
    $db = get_db();

    $stmt = $db->prepare("
        SELECT a.id,
               a.account_number,
               a.holder_name,
               a.account_type,
               a.balance,
               COUNT(t.id) AS transaction_count,
               COALESCE(SUM(CASE WHEN t.transaction_type = 'deposit' THEN t.amount ELSE 0 END), 0) AS total_deposited
        FROM accounts a
        LEFT JOIN transactions t ON t.account_id = a.id
        WHERE a.is_active = TRUE
        GROUP BY a.id
        ORDER BY a.balance DESC
        LIMIT :lim
    ");
    $stmt->bindValue('lim', $limit, PDO::PARAM_INT);
    $stmt->execute();

    json_response($stmt->fetchAll());
}

/**
 * GET /api/dashboard/monthly-growth/
 */
function handle_monthly_growth(): void
{
    $db = get_db();
    $rows = $db->query("
        SELECT TO_CHAR(DATE_TRUNC('month', date), 'YYYY-MM') AS month,
               COUNT(*) AS count,
               SUM(amount) AS total
        FROM transactions
        GROUP BY DATE_TRUNC('month', date)
        ORDER BY DATE_TRUNC('month', date)
    ")->fetchAll();

    $n = count($rows);
    if ($n < 2) {
        json_response([
            'current' => 0, 'previous' => 0,
            'change' => 0, 'change_pct' => 0,
        ]);
        return;
    }

    $current  = (float)$rows[$n - 1]['total'];
    $previous = (float)$rows[$n - 2]['total'];
    $change   = $current - $previous;
    $pct      = $previous != 0 ? round(($change / $previous) * 100, 2) : 0;

    json_response([
        'current_month'  => $rows[$n - 1]['month'],
        'previous_month' => $rows[$n - 2]['month'],
        'current'        => $current,
        'previous'       => $previous,
        'change'         => $change,
        'change_pct'     => $pct,
    ]);
}
