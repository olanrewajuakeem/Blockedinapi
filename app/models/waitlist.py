from app import db
from datetime import datetime

class Waitlist(db.Model):
    __tablename__ = 'waitlist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    ip_address = db.Column(db.String(45), nullable=True)
    expected_role = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'ip_address': self.ip_address,
            'expected_role': self.expected_role,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
