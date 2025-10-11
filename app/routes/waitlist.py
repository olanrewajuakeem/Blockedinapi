from flask import request
from flask_restx import Namespace, Resource, fields
from app import db
from app.models.waitlist import Waitlist

waitlist_ns = Namespace('waitlist', description='Waitlist API')

waitlist_model = waitlist_ns.model('Waitlist', {
    'name': fields.String(required=True, description='Full name'),
    'email': fields.String(required=True, description='Email address'),
    'ip_address': fields.String(required=True, description='IP address'),
    'expected_role': fields.String(required=True, description='Expected role (provider/hirer)'),
})

@waitlist_ns.route('/')
class WaitlistResource(Resource):
    @waitlist_ns.expect(waitlist_model)
    @waitlist_ns.response(201, 'Successfully added to waitlist')
    def post(self):
        """Add a new user to the waitlist"""
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        ip_address = data.get('ip_address')
        expected_role = data.get('expected_role')

        if not all([name, email, ip_address, expected_role]):
            return {'message': 'All fields (name, email, ip_address, expected_role) are required.'}, 400

        # Prevent duplicate emails
        if Waitlist.query.filter_by(email=email).first():
            return {'message': 'Email already exists in waitlist.'}, 409

        new_entry = Waitlist(
            name=name,
            email=email,
            ip_address=ip_address,
            expected_role=expected_role.lower()
        )

        db.session.add(new_entry)
        db.session.commit()

        return {'message': 'Successfully added to waitlist.'}, 201

    @waitlist_ns.response(200, 'Success')
    def get(self):
        """Fetch all waitlist entries"""
        entries = Waitlist.query.all()
        return [entry.to_dict() for entry in entries], 200
