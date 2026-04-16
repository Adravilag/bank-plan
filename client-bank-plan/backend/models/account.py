from datetime import datetime, timezone

from extensions import db


class Account(db.Model):
    __tablename__ = 'accounts'

    ACCOUNT_TYPES = ('savings', 'checking', 'credit', 'investment')

    id = db.Column(db.Integer, primary_key=True)
    account_number = db.Column(db.String(20), unique=True, nullable=False)
    holder_name = db.Column(db.String(200), nullable=False)
    account_type = db.Column(db.String(20), nullable=False)
    balance = db.Column(db.Numeric(15, 2), default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    is_active = db.Column(db.Boolean, default=True)

    transactions = db.relationship('Transaction', backref='account', lazy='dynamic')
    loans = db.relationship('Loan', backref='account', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'account_number': self.account_number,
            'holder_name': self.holder_name,
            'account_type': self.account_type,
            'balance': float(self.balance),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active,
        }

    def __repr__(self):
        return f"<Account {self.holder_name} - {self.account_number}>"
