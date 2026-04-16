<?php
/**
 * CRUD genérico para Accounts.
 * GET    /api/accounts/       → listar
 * POST   /api/accounts/       → crear
 * GET    /api/accounts/{id}/  → detalle
 * PUT    /api/accounts/{id}/  → actualizar
 * PATCH  /api/accounts/{id}/  → actualizar parcial
 * DELETE /api/accounts/{id}/  → eliminar
 */

require_once __DIR__ . '/../config/database.php';
require_once __DIR__ . '/../config/helpers.php';

function handle_accounts(array $segments): void
{
    $method = request_method();
    $id = $segments[1] ?? null;
    $db = get_db();

    // Listar todas
    if ($id === null && $method === 'GET') {
        $stmt = $db->query('SELECT * FROM accounts ORDER BY id');
        json_response($stmt->fetchAll());
    }

    // Crear
    if ($id === null && $method === 'POST') {
        $data = json_body();
        $stmt = $db->prepare('
            INSERT INTO accounts (account_number, holder_name, account_type, balance, is_active)
            VALUES (:account_number, :holder_name, :account_type, :balance, :is_active)
            RETURNING *
        ');
        $stmt->execute([
            'account_number' => $data['account_number'] ?? '',
            'holder_name'    => $data['holder_name'] ?? '',
            'account_type'   => $data['account_type'] ?? 'savings',
            'balance'        => $data['balance'] ?? 0,
            'is_active'      => isset($data['is_active']) ? ($data['is_active'] ? 'true' : 'false') : 'true',
        ]);
        json_response($stmt->fetch(), 201);
    }

    // Detalle
    if ($id !== null && $method === 'GET') {
        $stmt = $db->prepare('SELECT * FROM accounts WHERE id = :id');
        $stmt->execute(['id' => (int)$id]);
        $row = $stmt->fetch();
        if (!$row) json_response(['detail' => 'Not found'], 404);
        json_response($row);
    }

    // Actualizar (PUT / PATCH)
    if ($id !== null && in_array($method, ['PUT', 'PATCH'])) {
        $data = json_body();

        // Obtener datos actuales para PATCH
        $stmt = $db->prepare('SELECT * FROM accounts WHERE id = :id');
        $stmt->execute(['id' => (int)$id]);
        $current = $stmt->fetch();
        if (!$current) json_response(['detail' => 'Not found'], 404);

        $merged = array_merge($current, $data);

        $stmt = $db->prepare('
            UPDATE accounts
            SET account_number = :account_number,
                holder_name    = :holder_name,
                account_type   = :account_type,
                balance        = :balance,
                is_active      = :is_active
            WHERE id = :id
            RETURNING *
        ');
        $stmt->execute([
            'account_number' => $merged['account_number'],
            'holder_name'    => $merged['holder_name'],
            'account_type'   => $merged['account_type'],
            'balance'        => $merged['balance'],
            'is_active'      => $merged['is_active'] ? 'true' : 'false',
            'id'             => (int)$id,
        ]);
        json_response($stmt->fetch());
    }

    // Eliminar
    if ($id !== null && $method === 'DELETE') {
        $stmt = $db->prepare('DELETE FROM accounts WHERE id = :id');
        $stmt->execute(['id' => (int)$id]);
        if ($stmt->rowCount() === 0) json_response(['detail' => 'Not found'], 404);
        http_response_code(204);
        exit;
    }

    json_response(['detail' => 'Method not allowed'], 405);
}
