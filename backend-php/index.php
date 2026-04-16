<?php
/**
 * Entry point — Router principal.
 * Ejecutar: php -S localhost:8000 index.php
 */

require_once __DIR__ . '/config/helpers.php';
require_once __DIR__ . '/controllers/accounts.php';
require_once __DIR__ . '/controllers/transactions.php';
require_once __DIR__ . '/controllers/loans.php';
require_once __DIR__ . '/controllers/analytics.php';
require_once __DIR__ . '/controllers/auth.php';

// CORS
cors_headers();

$segments = parse_path();
$resource = $segments[0] ?? '';

// Routing
switch ($resource) {
    // CRUD
    case 'accounts':
        handle_accounts($segments);
        break;

    case 'transactions':
        handle_transactions($segments);
        break;

    case 'loans':
        handle_loans($segments);
        break;

    // Auth
    case 'auth':
        $action = $segments[1] ?? '';
        if ($action === 'login') {
            handle_login();
        }
        json_response(['detail' => 'Not found'], 404);
        break;

    // Analytics
    case 'dashboard':
        $action = $segments[1] ?? '';
        $analytics_map = [
            'summary'                => 'handle_dashboard_summary',
            'transactions-by-type'   => 'handle_transactions_by_type',
            'transactions-by-month'  => 'handle_transactions_by_month',
            'balance-by-account-type'=> 'handle_balance_by_account_type',
            'loan-summary'           => 'handle_loan_summary',
            'cash-flow'              => 'handle_cash_flow',
            'top-accounts'           => 'handle_top_accounts',
            'monthly-growth'         => 'handle_monthly_growth',
        ];

        if (isset($analytics_map[$action]) && request_method() === 'GET') {
            $analytics_map[$action]();
        }

        json_response(['detail' => 'Not found'], 404);
        break;

    default:
        json_response(['detail' => 'Not found'], 404);
}
