from app.db import db
from datetime import datetime

class Dispute(db.Model):
    __tablename__ = 'disputes'
    id = db.Column(db.Integer, primary_key=True)
    gig_id = db.Column(db.String(255), nullable=False)
    initiator_uid = db.Column(db.String(255), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default='pending') 
    resolution = db.Column(db.Text)
    outcome = db.Column(db.String(50)) 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)