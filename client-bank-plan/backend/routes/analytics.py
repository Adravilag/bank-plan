from flask import Blueprint, request, jsonify

from services.analytics import (
    get_dashboard_summary,
    get_transactions_by_type,
    get_transactions_by_month,
    get_balance_by_account_type,
    get_loan_summary,
    get_cash_flow_by_month,
    get_top_accounts,
    get_monthly_growth,
)

analytics_bp = Blueprint('analytics', __name__)


@analytics_bp.route('/dashboard/summary/', methods=['GET'])
def dashboard_summary():
    return jsonify(get_dashboard_summary())


@analytics_bp.route('/dashboard/transactions-by-type/', methods=['GET'])
def transactions_by_type():
    return jsonify(get_transactions_by_type())


@analytics_bp.route('/dashboard/transactions-by-month/', methods=['GET'])
def transactions_by_month():
    return jsonify(get_transactions_by_month())


@analytics_bp.route('/dashboard/balance-by-account-type/', methods=['GET'])
def balance_by_account_type():
    return jsonify(get_balance_by_account_type())


@analytics_bp.route('/dashboard/loan-summary/', methods=['GET'])
def loan_summary():
    return jsonify(get_loan_summary())


@analytics_bp.route('/dashboard/cash-flow/', methods=['GET'])
def cash_flow_by_month():
    return jsonify(get_cash_flow_by_month())


@analytics_bp.route('/dashboard/top-accounts/', methods=['GET'])
def top_accounts():
    limit = request.args.get('limit', 10, type=int)
    return jsonify(get_top_accounts(min(limit, 50)))


@analytics_bp.route('/dashboard/monthly-growth/', methods=['GET'])
def monthly_growth():
    return jsonify(get_monthly_growth())
