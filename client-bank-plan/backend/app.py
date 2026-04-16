from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO

from config import Config
from extensions import db, socketio
from models import Account, Transaction, Loan


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Extensions
    db.init_app(app)
    CORS(app, origins=app.config['CORS_ORIGINS'])
    socketio.init_app(app, cors_allowed_origins=app.config['CORS_ORIGINS'])

    # Blueprints
    from routes.accounts import accounts_bp
    from routes.transactions import transactions_bp
    from routes.loans import loans_bp
    from routes.auth import auth_bp
    from routes.analytics import analytics_bp

    app.register_blueprint(accounts_bp, url_prefix='/api')
    app.register_blueprint(transactions_bp, url_prefix='/api')
    app.register_blueprint(loans_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(analytics_bp, url_prefix='/api')

    # Dash micro-frontend
    from dash_app import create_dash_app
    create_dash_app(app)

    # WebSocket events
    from websocket_events import register_events
    register_events(socketio)

    # Create tables
    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == '__main__':
    socketio.run(app, debug=True, port=8000)
