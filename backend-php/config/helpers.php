<?php
/**
 * Helpers: JSON response, CORS y routing básico.
 */

/**
 * Envía cabeceras CORS para permitir requests desde el frontend Angular.
 */
function cors_headers(): void
{
    $origin = $_SERVER['HTTP_ORIGIN'] ?? '';
    $allowed = ['http://localhost:4200'];

    if (in_array($origin, $allowed, true)) {
        header("Access-Control-Allow-Origin: $origin");
    }

    header('Access-Control-Allow-Methods: GET, POST, PUT, PATCH, DELETE, OPTIONS');
    header('Access-Control-Allow-Headers: Content-Type, Authorization');
    header('Access-Control-Max-Age: 86400');

    // Preflight
    if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
        http_response_code(204);
        exit;
    }
}

/**
 * Envía una respuesta JSON y termina la ejecución.
 */
function json_response($data, int $status = 200): void
{
    http_response_code($status);
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode($data, JSON_UNESCAPED_UNICODE | JSON_NUMERIC_CHECK);
    exit;
}

/**
 * Lee el body JSON del request.
 */
function json_body(): array
{
    $raw = file_get_contents('php://input');
    $data = json_decode($raw, true);
    return is_array($data) ? $data : [];
}

/**
 * Obtiene el método HTTP real.
 */
function request_method(): string
{
    return $_SERVER['REQUEST_METHOD'];
}

/**
 * Parsea la URI y devuelve los segmentos del path después de /api/.
 * Ejemplo: /api/accounts/5 → ['accounts', '5']
 */
function parse_path(): array
{
    $uri = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
    $uri = trim($uri, '/');

    // Quitar prefijo "api"
    if (str_starts_with($uri, 'api/')) {
        $uri = substr($uri, 4);
    }

    $uri = trim($uri, '/');
    return $uri !== '' ? explode('/', $uri) : [];
}
