<?php
/**
 * POST /api/auth/login/
 * Body: { "username": "...", "password": "..." }
 */

require_once __DIR__ . '/../config/database.php';
require_once __DIR__ . '/../config/helpers.php';

function handle_login(): void
{
    if (request_method() !== 'POST') {
        json_response(['detail' => 'Method not allowed'], 405);
    }

    $data = json_body();
    $username = trim($data['username'] ?? '');
    $password = $data['password'] ?? '';

    if ($username === '' || $password === '') {
        json_response(['error' => 'Usuario y contraseña son requeridos'], 400);
    }

    $db = get_db();
    $stmt = $db->prepare('SELECT * FROM users WHERE username = :username');
    $stmt->execute(['username' => $username]);
    $user = $stmt->fetch();

    if (!$user || !password_verify($password, $user['password'])) {
        json_response(['error' => 'Credenciales inválidas'], 401);
    }

    $token = hash('sha256', random_bytes(32));

    json_response([
        'token' => $token,
        'user'  => [
            'id'       => (int)$user['id'],
            'username' => $user['username'],
        ],
    ]);
}
