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

    def __repr__(self):
        return f"<Waitlist {self.email}>"
