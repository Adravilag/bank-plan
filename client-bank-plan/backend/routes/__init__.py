from .accounts import accounts_bp
from .transactions import transactions_bp
from .loans import loans_bp
from .auth import auth_bp
from .analytics import analytics_bp

__all__ = ['accounts_bp', 'transactions_bp', 'loans_bp', 'auth_bp', 'analytics_bp']
