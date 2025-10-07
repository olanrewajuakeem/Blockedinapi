from app.db import db
from datetime import datetime
import uuid

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

    @staticmethod
    def create_gig(provider_uid, title, price, duration_hours, gig_id=None, status='pending'):
        if gig_id and Gig.query.filter_by(gig_id=gig_id).first():
            return None
        gig = Gig(
            gig_id=gig_id or f"gig_{uuid.uuid4().hex[:8]}",
            provider_uid=provider_uid,
            title=title,
            price=price,
            duration_hours=duration_hours,
            status=status,
            created_at=datetime.utcnow()
        )
        db.session.add(gig)
        db.session.commit()
        return {
            'id': gig.id,
            'gig_id': gig.gig_id,
            'provider_uid': gig.provider_uid,
            'title': gig.title,
            'price': gig.price,
            'duration_hours': gig.duration_hours,
            'status': gig.status,
            'created_at': gig.created_at.isoformat()
        }