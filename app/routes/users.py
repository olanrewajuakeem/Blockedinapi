from flask_restx import Namespace, Resource, fields
from app.models import User
from app.db import db

users_ns = Namespace('users', description='User operations')

# Define the expected input model
user_model = users_ns.model('User', {
    'uid': fields.String(required=True, description='Unique user identifier'),
    'email': fields.String(required=True, description='User email address'),
    'wallet_address': fields.String(required=True, description='Blockchain wallet address'),
    'role': fields.String(enum=['hirer', 'provider', 'both'], default='both', description='User role')
})

@users_ns.route('')
class Users(Resource):
    @users_ns.expect(user_model)
    def post(self):
        """Register a new user"""
        data = users_ns.payload

        # Prevent duplicate UID or email
        if User.query.filter((User.uid == data['uid']) | (User.email == data['email'])).first():
            return {'error': 'User with this UID or email already exists'}, 400

        try:
            user = User(
                uid=data['uid'],
                email=data['email'],
                wallet_address=data['wallet_address'],
                role=data.get('role', 'both')
            )
            db.session.add(user)
            db.session.commit()

            return {
                'id': user.id,
                'uid': user.uid,
                'email': user.email,
                'wallet_address': user.wallet_address,
                'role': user.role
            }, 201

        except Exception as e:
            db.session.rollback()
            return {'error': f'Database error: {str(e)}'}, 500

    def get(self):
        """Get all users"""
        users = User.query.all()
        return [
            {
                'id': u.id,
                'uid': u.uid,
                'email': u.email,
                'wallet_address': u.wallet_address,
                'role': u.role
            } for u in users
        ]
