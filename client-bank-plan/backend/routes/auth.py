import hashlib
import secrets

from flask import Blueprint, request, jsonify

auth_bp = Blueprint('auth', __name__)

# Simple in-memory users for demo (in production use a proper user model)
DEMO_USERS = {
    'admin': {
        'id': 1,
        'username': 'admin',
        'password_hash': hashlib.sha256('admin123'.encode()).hexdigest(),
    }
}


@auth_bp.route('/auth/login/', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username', '')
    password = data.get('password', '')

    if not username or not password:
        return jsonify({'error': 'Usuario y contraseña son requeridos'}), 400

    user = DEMO_USERS.get(username)
    password_hash = hashlib.sha256(password.encode()).hexdigest()

    if user is None or user['password_hash'] != password_hash:
        return jsonify({'error': 'Credenciales inválidas'}), 401

    raw_token = secrets.token_hex(32)
    token = hashlib.sha256(raw_token.encode()).hexdigest()

    return jsonify({
        'token': token,
        'user': {
            'id': user['id'],
            'username': user['username'],
        },
    })
