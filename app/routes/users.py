from flask_restx import Namespace, Resource, fields
from app.models import User
from app.db import db

users_ns = Namespace('user', description='User operations')

# --- Models ---

user_model = users_ns.model('User', {
    'firstname': fields.String(required=True),
    'lastname': fields.String(required=True),
    'email': fields.String(required=True),
    'wallet_address': fields.String(required=True),
    'is_provider': fields.Boolean(default=False),
    'is_admin': fields.Boolean(default=False),
    'is_mod': fields.Boolean(default=False),
    'bio': fields.String(),
    'skills': fields.String(),
    'company': fields.String(),
    'category': fields.String(),
    'social_x': fields.String(),
    'age': fields.Integer(),
    'country': fields.String(),
    'portfolio': fields.String(description='CV/Portfolio URL'),
    'profile_image': fields.String(description='Profile image URL')
})

update_model = users_ns.clone('UpdateUser', user_model)

query_model = users_ns.model('QueryUser', {
    'uid': fields.String(),
    'firstname': fields.String(),
    'lastname': fields.String(),
    'email': fields.String(),
    'wallet_address': fields.String(),
    'is_provider': fields.Boolean(),
    'is_admin': fields.Boolean(),
    'is_mod': fields.Boolean(),
    'category': fields.String(),
    'country': fields.String()
})

# --- Routes ---

@users_ns.route('/')
class Users(Resource):
    @users_ns.expect(user_model)
    def post(self):
        """Register a new user"""
        data = users_ns.payload
        if User.query.filter_by(email=data['email']).first():
            return {'error': 'Email already exists'}, 400
        if User.query.filter_by(wallet_address=data['wallet_address']).first():
            return {'error': 'Wallet address already exists'}, 400

        try:
            user = User.create_user(**data)
            return user, 201
        except Exception as e:
            db.session.rollback()
            return {'error': f'Database error: {str(e)}'}, 500

    def get(self):
        """Get all users"""
        users = User.query.all()
        return [u.to_dict() for u in users], 200


@users_ns.route('/<string:uid>')
class UserById(Resource):
    def get(self, uid):
        """Get user by UID"""
        user = User.query.filter_by(uid=uid).first()
        if not user:
            return {'error': 'User not found'}, 404
        return user.to_dict(), 200

    @users_ns.expect(update_model)
    def put(self, uid):
        """Update user by UID"""
        user = User.query.filter_by(uid=uid).first()
        if not user:
            return {'error': 'User not found'}, 404
        data = users_ns.payload

        if 'email' in data and data['email'] != user.email and User.query.filter_by(email=data['email']).first():
            return {'error': 'Email already exists'}, 400
        if 'wallet_address' in data and data['wallet_address'] != user.wallet_address and User.query.filter_by(wallet_address=data['wallet_address']).first():
            return {'error': 'Wallet address already exists'}, 400

        try:
            for key, value in data.items():
                setattr(user, key, value)
            db.session.commit()
            return user.to_dict(), 200
        except Exception as e:
            db.session.rollback()
            return {'error': f'Database error: {str(e)}'}, 500

    def delete(self, uid):
        """Delete user by UID"""
        user = User.query.filter_by(uid=uid).first()
        if not user:
            return {'error': 'User not found'}, 404
        try:
            db.session.delete(user)
            db.session.commit()
            return {'message': 'User deleted successfully'}, 200
        except Exception as e:
            db.session.rollback()
            return {'error': f'Database error: {str(e)}'}, 500


@users_ns.route('/query')
class UserQuery(Resource):
    @users_ns.expect(query_model)
    def post(self):
        """Query users by any field"""
        data = users_ns.payload
        query = User.query
        for key, value in data.items():
            if value is not None:
                query = query.filter(getattr(User, key) == value)
        users = query.all()
        if not users:
            return {'error': 'No users found'}, 404
        return [u.to_dict() for u in users], 200
