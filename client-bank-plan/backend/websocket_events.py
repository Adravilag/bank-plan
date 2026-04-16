from flask_socketio import SocketIO, emit

from services.analytics import get_dashboard_summary, get_cash_flow_by_month


def register_events(socketio: SocketIO):
    """Register WebSocket events for real-time dashboard communication with Angular."""

    @socketio.on('connect', namespace='/dashboard')
    def handle_connect():
        """Client connected — send initial dashboard data."""
        from flask import current_app
        with current_app.app_context():
            summary = get_dashboard_summary()
            cash_flow = get_cash_flow_by_month()
        emit('dashboard_update', {
            'summary': summary,
            'cash_flow': cash_flow,
        })

    @socketio.on('disconnect', namespace='/dashboard')
    def handle_disconnect():
        pass

    @socketio.on('request_update', namespace='/dashboard')
    def handle_request_update():
        """Angular client requests fresh dashboard data."""
        from flask import current_app
        with current_app.app_context():
            summary = get_dashboard_summary()
            cash_flow = get_cash_flow_by_month()
        emit('dashboard_update', {
            'summary': summary,
            'cash_flow': cash_flow,
        })

    @socketio.on('request_chart', namespace='/dashboard')
    def handle_request_chart(data):
        """Angular client requests a specific chart's data."""
        from flask import current_app
        from services.analytics import (
            get_transactions_by_type,
            get_transactions_by_month,
            get_balance_by_account_type,
            get_loan_summary,
        )
        chart_type = data.get('chart', '')
        chart_handlers = {
            'transactions_by_type': get_transactions_by_type,
            'transactions_by_month': get_transactions_by_month,
            'balance_by_account_type': get_balance_by_account_type,
            'loan_summary': get_loan_summary,
            'cash_flow': get_cash_flow_by_month,
        }
        handler = chart_handlers.get(chart_type)
        if handler:
            with current_app.app_context():
                result = handler()
            emit('chart_data', {'chart': chart_type, 'data': result})
