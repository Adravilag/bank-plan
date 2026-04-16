from flask import Blueprint, request, jsonify

from extensions import db
from models import Account

accounts_bp = Blueprint('accounts', __name__)


@accounts_bp.route('/accounts/', methods=['GET'])
def list_accounts():
    accounts = Account.query.all()
    return jsonify([a.to_dict() for a in accounts])


@accounts_bp.route('/accounts/<int:pk>/', methods=['GET'])
def get_account(pk):
    account = db.get_or_404(Account, pk)
    return jsonify(account.to_dict())


@accounts_bp.route('/accounts/', methods=['POST'])
def create_account():
    data = request.get_json()
    account = Account(
        account_number=data['account_number'],
        holder_name=data['holder_name'],
        account_type=data['account_type'],
        balance=data.get('balance', 0),
        is_active=data.get('is_active', True),
    )
    db.session.add(account)
    db.session.commit()
    return jsonify(account.to_dict()), 201


@accounts_bp.route('/accounts/<int:pk>/', methods=['PUT'])
def update_account(pk):
    account = db.get_or_404(Account, pk)
    data = request.get_json()
    for field in ('account_number', 'holder_name', 'account_type', 'balance', 'is_active'):
        if field in data:
            setattr(account, field, data[field])
    db.session.commit()
    return jsonify(account.to_dict())


@accounts_bp.route('/accounts/<int:pk>/', methods=['PATCH'])
def partial_update_account(pk):
    account = db.get_or_404(Account, pk)
    data = request.get_json()
    for field in ('account_number', 'holder_name', 'account_type', 'balance', 'is_active'):
        if field in data:
            setattr(account, field, data[field])
    db.session.commit()
    return jsonify(account.to_dict())


@accounts_bp.route('/accounts/<int:pk>/', methods=['DELETE'])
def delete_account(pk):
    account = db.get_or_404(Account, pk)
    db.session.delete(account)
    db.session.commit()
    return '', 204
