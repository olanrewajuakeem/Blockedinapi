from app.db import db
from datetime import datetime

class Escrow(db.Model):
    __tablename__ = 'escrow'
    id = db.Column(db.Integer, primary_key=True)
    gig_id = db.Column(db.String(255), unique=True, nullable=False)
    provider_address = db.Column(db.String(42), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='funded')
    tx_hash = db.Column(db.String(66))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)