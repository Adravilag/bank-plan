from flask import Blueprint, request, jsonify

from extensions import db
from models import Transaction

transactions_bp = Blueprint('transactions', __name__)


@transactions_bp.route('/transactions/', methods=['GET'])
def list_transactions():
    qs = Transaction.query
    account_id = request.args.get('account')
    if account_id:
        qs = qs.filter_by(account_id=account_id)
    transactions = qs.order_by(Transaction.date.desc()).all()
    return jsonify([t.to_dict() for t in transactions])


@transactions_bp.route('/transactions/<int:pk>/', methods=['GET'])
def get_transaction(pk):
    txn = db.get_or_404(Transaction, pk)
    return jsonify(txn.to_dict())


@transactions_bp.route('/transactions/', methods=['POST'])
def create_transaction():
    data = request.get_json()
    from datetime import datetime
    txn = Transaction(
        account_id=data['account'],
        transaction_type=data['transaction_type'],
        amount=data['amount'],
        description=data.get('description', ''),
        date=datetime.fromisoformat(data['date']),
        category=data.get('category', ''),
    )
    db.session.add(txn)
    db.session.commit()

    # Emit WebSocket event for real-time dashboard updates
    from extensions import socketio
    socketio.emit('transaction_created', txn.to_dict(), namespace='/dashboard')

    return jsonify(txn.to_dict()), 201


@transactions_bp.route('/transactions/<int:pk>/', methods=['PUT'])
def update_transaction(pk):
    txn = db.get_or_404(Transaction, pk)
    data = request.get_json()
    from datetime import datetime
    for field in ('transaction_type', 'amount', 'description', 'category'):
        if field in data:
            setattr(txn, field, data[field])
    if 'account' in data:
        txn.account_id = data['account']
    if 'date' in data:
        txn.date = datetime.fromisoformat(data['date'])
    db.session.commit()
    return jsonify(txn.to_dict())


@transactions_bp.route('/transactions/<int:pk>/', methods=['PATCH'])
def partial_update_transaction(pk):
    txn = db.get_or_404(Transaction, pk)
    data = request.get_json()
    from datetime import datetime
    for field in ('transaction_type', 'amount', 'description', 'category'):
        if field in data:
            setattr(txn, field, data[field])
    if 'account' in data:
        txn.account_id = data['account']
    if 'date' in data:
        txn.date = datetime.fromisoformat(data['date'])
    db.session.commit()
    return jsonify(txn.to_dict())


@transactions_bp.route('/transactions/<int:pk>/', methods=['DELETE'])
def delete_transaction(pk):
    txn = db.get_or_404(Transaction, pk)
    db.session.delete(txn)
    db.session.commit()
    return '', 204
