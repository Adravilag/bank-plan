<?php
/**
 * CRUD para Loans.
 */

require_once __DIR__ . '/../config/database.php';
require_once __DIR__ . '/../config/helpers.php';

function handle_loans(array $segments): void
{
    $method = request_method();
    $id = $segments[1] ?? null;
    $db = get_db();

    // Listar
    if ($id === null && $method === 'GET') {
        $stmt = $db->query('SELECT * FROM loans ORDER BY id');
        json_response($stmt->fetchAll());
    }

    // Crear
    if ($id === null && $method === 'POST') {
        $data = json_body();
        $stmt = $db->prepare('
            INSERT INTO loans (account_id, amount, interest_rate, term_months, monthly_payment, remaining_balance, status, start_date)
            VALUES (:account_id, :amount, :interest_rate, :term_months, :monthly_payment, :remaining_balance, :status, :start_date)
            RETURNING *
        ');
        $stmt->execute([
            'account_id'        => (int)($data['account'] ?? $data['account_id'] ?? 0),
            'amount'            => $data['amount'] ?? 0,
            'interest_rate'     => $data['interest_rate'] ?? 0,
            'term_months'       => (int)($data['term_months'] ?? 0),
            'monthly_payment'   => $data['monthly_payment'] ?? 0,
            'remaining_balance' => $data['remaining_balance'] ?? 0,
            'status'            => $data['status'] ?? 'active',
            'start_date'        => $data['start_date'] ?? date('Y-m-d'),
        ]);
        json_response($stmt->fetch(), 201);
    }

    // Detalle
    if ($id !== null && $method === 'GET') {
        $stmt = $db->prepare('SELECT * FROM loans WHERE id = :id');
        $stmt->execute(['id' => (int)$id]);
        $row = $stmt->fetch();
        if (!$row) json_response(['detail' => 'Not found'], 404);
        json_response($row);
    }

    // Actualizar
    if ($id !== null && in_array($method, ['PUT', 'PATCH'])) {
        $data = json_body();

        $stmt = $db->prepare('SELECT * FROM loans WHERE id = :id');
        $stmt->execute(['id' => (int)$id]);
        $current = $stmt->fetch();
        if (!$current) json_response(['detail' => 'Not found'], 404);

        $merged = array_merge($current, $data);

        $stmt = $db->prepare('
            UPDATE loans
            SET account_id        = :account_id,
                amount            = :amount,
                interest_rate     = :interest_rate,
                term_months       = :term_months,
                monthly_payment   = :monthly_payment,
                remaining_balance = :remaining_balance,
                status            = :status,
                start_date        = :start_date
            WHERE id = :id
            RETURNING *
        ');
        $stmt->execute([
            'account_id'        => (int)$merged['account_id'],
            'amount'            => $merged['amount'],
            'interest_rate'     => $merged['interest_rate'],
            'term_months'       => (int)$merged['term_months'],
            'monthly_payment'   => $merged['monthly_payment'],
            'remaining_balance' => $merged['remaining_balance'],
            'status'            => $merged['status'],
            'start_date'        => $merged['start_date'],
            'id'                => (int)$id,
        ]);
        json_response($stmt->fetch());
    }

    // Eliminar
    if ($id !== null && $method === 'DELETE') {
        $stmt = $db->prepare('DELETE FROM loans WHERE id = :id');
        $stmt->execute(['id' => (int)$id]);
        if ($stmt->rowCount() === 0) json_response(['detail' => 'Not found'], 404);
        http_response_code(204);
        exit;
    }

    json_response(['detail' => 'Method not allowed'], 405);
}
