<?php
/**
 * Genera datos de prueba para el dashboard bancario.
 * Ejecutar: php seed.php
 */

require_once __DIR__ . '/config/database.php';

$db = get_db();

echo "Limpiando datos existentes...\n";
$db->exec('DELETE FROM transactions');
$db->exec('DELETE FROM loans');
$db->exec('DELETE FROM accounts');
$db->exec('DELETE FROM users');

// --- Usuario admin ---
$hash = password_hash('admin123', PASSWORD_BCRYPT);
$stmt = $db->prepare("INSERT INTO users (username, password) VALUES ('admin', :pass)");
$stmt->execute(['pass' => $hash]);
echo "Usuario admin creado (admin / admin123)\n";

// --- Cuentas ---
$names = [
    'Carlos García', 'María López', 'Juan Martínez', 'Ana Rodríguez',
    'Pedro Sánchez', 'Laura Fernández', 'Miguel Torres', 'Sofía Ruiz',
    'Diego Herrera', 'Valentina Castro', 'Andrés Morales', 'Camila Vargas',
    'Luis Ramírez', 'Isabella Flores', 'Mateo Jiménez', 'Daniela Reyes',
    'Sebastián Díaz', 'Paula Mendoza', 'Nicolás Ortiz', 'Gabriela Romero',
];
$account_types = ['savings', 'checking', 'credit', 'investment'];

$stmt = $db->prepare("
    INSERT INTO accounts (account_number, holder_name, account_type, balance, is_active)
    VALUES (:num, :name, :type, :balance, :active)
");

$account_ids = [];
foreach ($names as $i => $name) {
    $num = sprintf('100%04d%04d', $i, random_int(1000, 9999));
    $type = $account_types[array_rand($account_types)];
    $balance = round(random_int(1000, 500000) + random_int(0, 99) / 100, 2);
    $active = random_int(1, 10) > 1; // 90% activas

    $stmt->execute([
        'num'     => $num,
        'name'    => $name,
        'type'    => $type,
        'balance' => $balance,
        'active'  => $active ? 'true' : 'false',
    ]);
    $account_ids[] = $db->lastInsertId();
}
echo count($account_ids) . " cuentas creadas\n";

// --- Transacciones (500, últimos 12 meses) ---
$tx_types = ['deposit', 'withdrawal', 'transfer', 'payment', 'fee'];
$categories = [
    'Nómina', 'Alimentos', 'Transporte', 'Servicios', 'Entretenimiento',
    'Educación', 'Salud', 'Inversión', 'Ahorro', 'Otros',
];

$now = time();
$stmt = $db->prepare("
    INSERT INTO transactions (account_id, transaction_type, amount, description, date, category)
    VALUES (:aid, :type, :amount, :desc, :date, :cat)
");

for ($i = 0; $i < 500; $i++) {
    $days_ago = random_int(0, 365);
    $hours = random_int(0, 23);
    $tx_date = date('Y-m-d H:i:s', $now - ($days_ago * 86400) - ($hours * 3600));
    $tx_type = $tx_types[array_rand($tx_types)];
    $amount = round(random_int(10, 50000) + random_int(0, 99) / 100, 2);

    $stmt->execute([
        'aid'    => $account_ids[array_rand($account_ids)],
        'type'   => $tx_type,
        'amount' => $amount,
        'desc'   => ucfirst($tx_type) . ' automático',
        'date'   => $tx_date,
        'cat'    => $categories[array_rand($categories)],
    ]);
}
echo "500 transacciones creadas\n";

// --- Préstamos (10) ---
$loan_statuses = ['active', 'active', 'active', 'paid', 'defaulted'];
$terms = [12, 24, 36, 48, 60];

$stmt = $db->prepare("
    INSERT INTO loans (account_id, amount, interest_rate, term_months, monthly_payment, remaining_balance, status, start_date)
    VALUES (:aid, :amount, :rate, :term, :monthly, :remaining, :status, :start)
");

$sample = array_rand(array_flip($account_ids), 10);
foreach ($sample as $aid) {
    $amount = round(random_int(5000, 200000) + random_int(0, 99) / 100, 2);
    $rate = round(random_int(500, 1800) / 100, 2);
    $term = $terms[array_rand($terms)];
    $monthly = round($amount * (1 + $rate / 100) / $term, 2);
    $status = $loan_statuses[array_rand($loan_statuses)];
    $remaining = $status === 'active'
        ? round($amount * (random_int(10, 90) / 100), 2)
        : 0;
    $days_ago = random_int(30, 730);
    $start = date('Y-m-d', $now - ($days_ago * 86400));

    $stmt->execute([
        'aid'       => $aid,
        'amount'    => $amount,
        'rate'      => $rate,
        'term'      => $term,
        'monthly'   => $monthly,
        'remaining' => $remaining,
        'status'    => $status,
        'start'     => $start,
    ]);
}
echo "10 préstamos creados\n";
echo "¡Datos de prueba generados correctamente!\n";
