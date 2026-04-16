<?php
/**
 * CRUD para Transactions.
 * Soporta filtro ?account={id}
 */

require_once __DIR__ . '/../config/database.php';
require_once __DIR__ . '/../config/helpers.php';

function handle_transactions(array $segments): void
{
    $method = request_method();
    $id = $segments[1] ?? null;
    $db = get_db();

    // Listar (con filtro opcional por account)
    if ($id === null && $method === 'GET') {
        $account_id = $_GET['account'] ?? null;
        if ($account_id !== null) {
            $stmt = $db->prepare('SELECT * FROM transactions WHERE account_id = :aid ORDER BY date DESC');
            $stmt->execute(['aid' => (int)$account_id]);
        } else {
            $stmt = $db->query('SELECT * FROM transactions ORDER BY date DESC');
        }
        json_response($stmt->fetchAll());
    }

    // Crear
    if ($id === null && $method === 'POST') {
        $data = json_body();
        $stmt = $db->prepare('
            INSERT INTO transactions (account_id, transaction_type, amount, description, date, category)
            VALUES (:account_id, :transaction_type, :amount, :description, :date, :category)
            RETURNING *
        ');
        $stmt->execute([
            'account_id'       => (int)($data['account'] ?? $data['account_id'] ?? 0),
            'transaction_type' => $data['transaction_type'] ?? '',
            'amount'           => $data['amount'] ?? 0,
            'description'      => $data['description'] ?? '',
            'date'             => $data['date'] ?? date('Y-m-d H:i:s'),
            'category'         => $data['category'] ?? '',
        ]);
        json_response($stmt->fetch(), 201);
    }

    // Detalle
    if ($id !== null && $method === 'GET') {
        $stmt = $db->prepare('SELECT * FROM transactions WHERE id = :id');
        $stmt->execute(['id' => (int)$id]);
        $row = $stmt->fetch();
        if (!$row) json_response(['detail' => 'Not found'], 404);
        json_response($row);
    }

    // Actualizar
    if ($id !== null && in_array($method, ['PUT', 'PATCH'])) {
        $data = json_body();

        $stmt = $db->prepare('SELECT * FROM transactions WHERE id = :id');
        $stmt->execute(['id' => (int)$id]);
        $current = $stmt->fetch();
        if (!$current) json_response(['detail' => 'Not found'], 404);

        $merged = array_merge($current, $data);

        $stmt = $db->prepare('
            UPDATE transactions
            SET account_id       = :account_id,
                transaction_type = :transaction_type,
                amount           = :amount,
                description      = :description,
                date             = :date,
                category         = :category
            WHERE id = :id
            RETURNING *
        ');
        $stmt->execute([
            'account_id'       => (int)$merged['account_id'],
            'transaction_type' => $merged['transaction_type'],
            'amount'           => $merged['amount'],
            'description'      => $merged['description'],
            'date'             => $merged['date'],
            'category'         => $merged['category'],
            'id'               => (int)$id,
        ]);
        json_response($stmt->fetch());
    }

    // Eliminar
    if ($id !== null && $method === 'DELETE') {
        $stmt = $db->prepare('DELETE FROM transactions WHERE id = :id');
        $stmt->execute(['id' => (int)$id]);
        if ($stmt->rowCount() === 0) json_response(['detail' => 'Not found'], 404);
        http_response_code(204);
        exit;
    }

    json_response(['detail' => 'Method not allowed'], 405);
}
