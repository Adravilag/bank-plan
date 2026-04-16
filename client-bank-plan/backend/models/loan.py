from extensions import db


class Loan(db.Model):
    __tablename__ = 'loans'

    LOAN_STATUSES = ('active', 'paid', 'defaulted')

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    interest_rate = db.Column(db.Numeric(5, 2), nullable=False)
    term_months = db.Column(db.Integer, nullable=False)
    monthly_payment = db.Column(db.Numeric(15, 2), nullable=False)
    remaining_balance = db.Column(db.Numeric(15, 2), nullable=False)
    status = db.Column(db.String(20), default='active')
    start_date = db.Column(db.Date, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'account': self.account_id,
            'amount': float(self.amount),
            'interest_rate': float(self.interest_rate),
            'term_months': self.term_months,
            'monthly_payment': float(self.monthly_payment),
            'remaining_balance': float(self.remaining_balance),
            'status': self.status,
            'start_date': self.start_date.isoformat() if self.start_date else None,
        }

    def __repr__(self):
        return f"<Loan €{self.amount} - {self.status}>"
