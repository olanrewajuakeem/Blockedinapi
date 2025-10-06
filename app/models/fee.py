from app.db import db
from datetime import datetime

class Fee(db.Model):
    __tablename__ = 'fees'
    id = db.Column(db.Integer, primary_key=True)
    gig_id = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @staticmethod
    def create_fee(gig_id, amount):
        fee = Fee(gig_id=gig_id, amount=float(amount))
        db.session.add(fee)
        db.session.commit()
        return {
            'id': fee.id,
            'gig_id': fee.gig_id,
            'amount': fee.amount,
            'created_at': fee.created_at.isoformat()
        }