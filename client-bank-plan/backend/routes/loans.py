from flask import Blueprint, request, jsonify

from extensions import db
from models import Loan

loans_bp = Blueprint('loans', __name__)


@loans_bp.route('/loans/', methods=['GET'])
def list_loans():
    loans = Loan.query.all()
    return jsonify([l.to_dict() for l in loans])


@loans_bp.route('/loans/<int:pk>/', methods=['GET'])
def get_loan(pk):
    loan = db.get_or_404(Loan, pk)
    return jsonify(loan.to_dict())


@loans_bp.route('/loans/', methods=['POST'])
def create_loan():
    data = request.get_json()
    from datetime import date, datetime
    start = data['start_date']
    if isinstance(start, str):
        start = date.fromisoformat(start)
    loan = Loan(
        account_id=data['account'],
        amount=data['amount'],
        interest_rate=data['interest_rate'],
        term_months=data['term_months'],
        monthly_payment=data['monthly_payment'],
        remaining_balance=data['remaining_balance'],
        status=data.get('status', 'active'),
        start_date=start,
    )
    db.session.add(loan)
    db.session.commit()
    return jsonify(loan.to_dict()), 201


@loans_bp.route('/loans/<int:pk>/', methods=['PUT'])
def update_loan(pk):
    loan = db.get_or_404(Loan, pk)
    data = request.get_json()
    from datetime import date
    for field in ('amount', 'interest_rate', 'term_months', 'monthly_payment', 'remaining_balance', 'status'):
        if field in data:
            setattr(loan, field, data[field])
    if 'account' in data:
        loan.account_id = data['account']
    if 'start_date' in data:
        loan.start_date = date.fromisoformat(data['start_date'])
    db.session.commit()
    return jsonify(loan.to_dict())


@loans_bp.route('/loans/<int:pk>/', methods=['PATCH'])
def partial_update_loan(pk):
    loan = db.get_or_404(Loan, pk)
    data = request.get_json()
    from datetime import date
    for field in ('amount', 'interest_rate', 'term_months', 'monthly_payment', 'remaining_balance', 'status'):
        if field in data:
            setattr(loan, field, data[field])
    if 'account' in data:
        loan.account_id = data['account']
    if 'start_date' in data:
        loan.start_date = date.fromisoformat(data['start_date'])
    db.session.commit()
    return jsonify(loan.to_dict())


@loans_bp.route('/loans/<int:pk>/', methods=['DELETE'])
def delete_loan(pk):
    loan = db.get_or_404(Loan, pk)
    db.session.delete(loan)
    db.session.commit()
    return '', 204
