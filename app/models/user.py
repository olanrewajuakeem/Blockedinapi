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
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    is_mod = db.Column(db.Boolean, nullable=False, default=False)
    bio = db.Column(db.Text, nullable=True)
    skills = db.Column(db.Text, nullable=True)
    company = db.Column(db.String(255), nullable=True)
    category = db.Column(db.String(255), nullable=True)
    social_x = db.Column(db.String(255), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    country = db.Column(db.String(255), nullable=True)
    portfolio = db.Column(db.String(512), nullable=True)  
    profile_image = db.Column(db.String(512), nullable=True)  

    # Rating fields
    total_rating = db.Column(db.Float, default=0.0)
    total_reviews = db.Column(db.Integer, default=0)
    rater_uid = db.Column(db.String(36), nullable=True)  

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @staticmethod
    def create_user(
        firstname, lastname, email, wallet_address,
        is_provider=False, is_admin=False, is_mod=False,
        bio=None, skills=None, company=None, category=None,
        social_x=None, age=None, country=None,
        portfolio=None, profile_image=None
    ):
        user = User(
            firstname=firstname,
            lastname=lastname,
            email=email,
            wallet_address=wallet_address,
            is_provider=is_provider,
            is_admin=is_admin,
            is_mod=is_mod,
            bio=bio,
            skills=skills,
            company=company,
            category=category,
            social_x=social_x,
            age=age,
            country=country,
            portfolio=portfolio,
            profile_image=profile_image
        )
        db.session.add(user)
        db.session.commit()
        return user.to_dict()

    def to_dict(self):
        return {
            'id': self.id,
            'uid': self.uid,
            'firstname': self.firstname,
            'lastname': self.lastname,
            'email': self.email,
            'wallet_address': self.wallet_address,
            'is_provider': self.is_provider,
            'is_admin': self.is_admin,
            'is_mod': self.is_mod,
            'bio': self.bio,
            'skills': self.skills,
            'company': self.company,
            'category': self.category,
            'social_x': self.social_x,
            'age': self.age,
            'country': self.country,
            'portfolio': self.portfolio,
            'profile_image': self.profile_image,
            'total_rating': self.total_rating,
            'total_reviews': self.total_reviews,
            'rater_uid': self.rater_uid,
            'created_at': self.created_at.isoformat()
        }
