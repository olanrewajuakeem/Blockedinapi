from flask_restx import Namespace, Resource, fields
from app.models import User
from app.db import db

users_ns = Namespace('users', description='User operations')

user_model = users_ns.model('User', {
    'firstname': fields.String(required=True, description='User first name'),
    'lastname': fields.String(required=True, description='User last name'),
    'email': fields.String(required=True, description='User email address'),
    'wallet_address': fields.String(required=True, description='Blockchain wallet address'),
    'is_provider': fields.Boolean(default=False, description='True for provider, False for hirer'),
    'bio': fields.String(description='Provider bio (optional)'),
    'skills': fields.String(description='Provider skills (optional)'),
    'company': fields.String(description='Hirer company (optional)'),
    'social_x': fields.String(description='X handle (optional)')
})

update_model = users_ns.model('UpdateUser', {
    'firstname': fields.String(description='User first name'),
    'lastname': fields.String(description='User last name'),
    'email': fields.String(description='User email address'),
    'wallet_address': fields.String(description='Blockchain wallet address'),
    'is_provider': fields.Boolean(description='True for provider, False for hirer'),
    'bio': fields.String(description='Provider bio'),
    'skills': fields.String(description='Provider skills'),
    'company': fields.String(description='Hirer company'),
    'social_x': fields.String(description='X handle')
})

query_model = users_ns.model('QueryUser', {
    'uid': fields.String(description='User UID'),
    'email': fields.String(description='User email'),
    'is_provider': fields.Boolean(description='True for providers, False for hirers')
})

@users_ns.route('')
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
            user = User.create_user(
                firstname=data['firstname'],
                lastname=data['lastname'],
                email=data['email'],
                wallet_address=data['wallet_address'],
                is_provider=data.get('is_provider', False),
                bio=data.get('bio'),
                skills=data.get('skills'),
                company=data.get('company'),
                social_x=data.get('social_x')
            )
            return user, 201
        except Exception as e:
            db.session.rollback()
            return {'error': f'Database error: {str(e)}'}, 500

    def get(self):
        """Get all users"""
        users = User.query.all()
        return [{
            'id': u.id,
            'uid': u.uid,
            'firstname': u.firstname,
            'lastname': u.lastname,
            'email': u.email,
            'wallet_address': u.wallet_address,
            'is_provider': u.is_provider,
            'bio': u.bio,
            'skills': u.skills,
            'company': u.company,
            'social_x': u.social_x,
            'created_at': u.created_at.isoformat()
        } for u in users]

@users_ns.route('/<string:uid>')
class UserById(Resource):
    def get(self, uid):
        """Get user by UID"""
        user = User.query.filter_by(uid=uid).first()
        if not user:
            return {'error': 'User not found'}, 404
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
            user.firstname = data.get('firstname', user.firstname)
            user.lastname = data.get('lastname', user.lastname)
            user.email = data.get('email', user.email)
            user.wallet_address = data.get('wallet_address', user.wallet_address)
            user.is_provider = data.get('is_provider', user.is_provider)
            user.bio = data.get('bio', user.bio)
            user.skills = data.get('skills', user.skills)
            user.company = data.get('company', user.company)
            user.social_x = data.get('social_x', user.social_x)
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
            }, 200
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
            return {'message': 'User deleted'}, 200
        except Exception as e:
            db.session.rollback()
            return {'error': f'Database error: {str(e)}'}, 500

@users_ns.route('/query')
class UserQuery(Resource):
    @users_ns.expect(query_model)
    def post(self):
        """Query users by UID, email, or is_provider"""
        data = users_ns.payload
        query = User.query
        if data.get('uid'):
            query = query.filter_by(uid=data['uid'])
        if data.get('email'):
            query = query.filter_by(email=data['email'])
        if 'is_provider' in data:
            query = query.filter_by(is_provider=data['is_provider'])
        users = query.all()
        if not users:
            return {'error': 'No users found'}, 404
        return [{
            'id': u.id,
            'uid': u.uid,
            'firstname': u.firstname,
            'lastname': u.lastname,
            'email': u.email,
            'wallet_address': u.wallet_address,
            'is_provider': u.is_provider,
            'bio': u.bio,
            'skills': u.skills,
            'company': u.company,
            'social_x': u.social_x,
            'created_at': u.created_at.isoformat()
        } for u in users]