from app.db import db
from datetime import datetime
import uuid

class Gig(db.Model):
    __tablename__ = 'gigs'
    id = db.Column(db.Integer, primary_key=True)
    gig_id = db.Column(db.String(255), unique=True, nullable=False, default=lambda: f"gig_{uuid.uuid4().hex[:8]}")
    provider_uid = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)
    duration_hours = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
