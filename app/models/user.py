from app.db import db
from app.db import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), nullable=False)
    wallet_address = db.Column(db.String(42), unique=True, nullable=False)
    role = db.Column(db.String(50), nullable=False, default='both')  
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @staticmethod
    def create_user(uid, wallet_address, role='both'):
        user = User(uid=uid, wallet_address=wallet_address, role=role)
        db.session.add(user)
        db.session.commit()
        return {
            'id': user.id,
            'uid': user.uid,
            'wallet_address': user.wallet_address,
            'role': user.role,
            'created_at': user.created_at.isoformat()
        }