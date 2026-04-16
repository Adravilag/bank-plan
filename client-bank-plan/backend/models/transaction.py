from extensions import db


class Transaction(db.Model):
    __tablename__ = 'transactions'

    TRANSACTION_TYPES = ('deposit', 'withdrawal', 'transfer', 'payment', 'fee')

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    description = db.Column(db.String(300), default='')
    date = db.Column(db.DateTime, nullable=False)
    category = db.Column(db.String(100), default='')

    def to_dict(self):
        return {
            'id': self.id,
            'account': self.account_id,
            'transaction_type': self.transaction_type,
            'amount': float(self.amount),
            'description': self.description,
            'date': self.date.isoformat() if self.date else None,
            'category': self.category,
        }

    def __repr__(self):
        return f"<Transaction {self.transaction_type} - €{self.amount}>"
