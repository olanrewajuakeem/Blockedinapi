from app.db import db
from datetime import datetime
import uuid

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    firstname = db.Column(db.String(255), nullable=False)
    lastname = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    wallet_address = db.Column(db.String(42), unique=True, nullable=False)
    is_provider = db.Column(db.Boolean, nullable=False, default=False)  
    bio = db.Column(db.Text, nullable=True)  
    skills = db.Column(db.Text, nullable=True)  
    company = db.Column(db.String(255), nullable=True)  
    social_x = db.Column(db.String(255), nullable=True)  
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @staticmethod
    def create_user(firstname, lastname, email, wallet_address, is_provider=False, bio=None, skills=None, company=None, social_x=None):
        user = User(
            firstname=firstname,
            lastname=lastname,
            email=email,
            wallet_address=wallet_address,
            is_provider=is_provider,
            bio=bio,
            skills=skills,
            company=company,
            social_x=social_x
        )
        db.session.add(user)
        db.session.commit()
        return {
            'id': user.id,
            'uid': user.uid,
            'firstname': user.firstname,
            'lastname': user.lastname,
            'email': user.email,
            'wallet_address': user.wallet_address,
            'is_provider': user.is_provider,
            'bio': user.bio,
            'skills': user.skills,
            'company': user.company,
            'social_x': user.social_x,
            'created_at': user.created_at.isoformat()
        }