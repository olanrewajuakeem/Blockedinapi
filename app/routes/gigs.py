from flask_restx import Namespace, Resource, fields
from app.models import Gig, User, GigInstance
from app.db import db
from sqlalchemy import or_

gigs_ns = Namespace('gigs', description='Gig operations')

gig_model = gigs_ns.model('Gig', {
    'gig_id': fields.String(required=False, description='Unique gig identifier (optional, auto-generated if not provided)'),
    'provider_uid': fields.String(required=True, description='Provider UID'),
    'title': fields.String(required=True, description='Gig title'),
    'price': fields.Float(required=True, description='Gig price in USDC'),
    'duration_hours': fields.Integer(required=True, description='Gig duration in hours')
})

update_gig_model = gigs_ns.model('UpdateGig', {
    'title': fields.String(description='Gig title'),
    'price': fields.Float(description='Gig price in USDC'),
    'duration_hours': fields.Integer(description='Gig duration in hours'),
    'status': fields.String(enum=['pending', 'active', 'completed', 'disputed'], description='Gig status')
})

query_gig_model = gigs_ns.model('QueryGig', {
    'title': fields.String(description='Partial match for gig title'),
    'price_min': fields.Float(description='Minimum price'),
    'price_max': fields.Float(description='Maximum price'),
    'duration_min': fields.Integer(description='Minimum duration in hours'),
    'duration_max': fields.Integer(description='Maximum duration in hours'),
    'status': fields.String(enum=['pending', 'active', 'completed', 'disputed'], description='Gig status'),
    'has_milestones': fields.Boolean(description='Filter gigs with milestones in GigInstance')
})

@gigs_ns.route('')
class Gigs(Resource):
    @gigs_ns.expect(gig_model)
    def post(self):
        """Create a new gig"""
        data = gigs_ns.payload
        gig_id = data.get('gig_id')
        if gig_id and Gig.query.filter_by(gig_id=gig_id).first():
            return {'error': 'Gig ID already exists'}, 400
        user = User.query.filter_by(uid=data['provider_uid']).first()
        if not user:
            return {"error": f"User not found for UID {data['provider_uid']}"}, 404
        if not user.is_provider:
            return {"error": "Only providers can create gigs"}, 403

        try:
            gig = Gig.create_gig(
                provider_uid=data['provider_uid'],
                title=data['title'],
                price=data['price'],
                duration_hours=data['duration_hours'],
                gig_id=gig_id
            )
            if not gig:
                return {'error': 'Failed to create gig'}, 400
            return gig, 201
        except Exception as e:
            db.session.rollback()
            return {'error': f'Database error: {str(e)}'}, 500

    def get(self):
        """Get all gigs"""
        gigs = Gig.query.all()
        return [{
            'id': g.id,
            'gig_id': g.gig_id,
            'provider_uid': g.provider_uid,
            'title': g.title,
            'price': g.price,
            'duration_hours': g.duration_hours,
            'status': g.status,
            'created_at': g.created_at.isoformat()
        } for g in gigs]

@gigs_ns.route('/<string:gig_id>')
class GigById(Resource):
    def get(self, gig_id):
        """Get gig by gig_id"""
        gig = Gig.query.filter_by(gig_id=gig_id).first()
        if not gig:
            return {'error': 'Gig not found'}, 404
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

    @gigs_ns.expect(update_gig_model)
    def put(self, gig_id):
        """Update gig by gig_id"""
        gig = Gig.query.filter_by(gig_id=gig_id).first()
        if not gig:
            return {'error': 'Gig not found'}, 404
        user = User.query.filter_by(uid=gig.provider_uid).first()
        if not user or not user.is_provider:
            return {'error': 'Only the provider can update this gig'}, 403
        if GigInstance.query.filter_by(gig_id=gig_id).first():
            return {'error': 'Cannot update gig with active instances'}, 400

        data = gigs_ns.payload
        try:
            gig.title = data.get('title', gig.title)
            gig.price = data.get('price', gig.price)
            gig.duration_hours = data.get('duration_hours', gig.duration_hours)
            gig.status = data.get('status', gig.status)
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
            }, 200
        except Exception as e:
            db.session.rollback()
            return {'error': f'Database error: {str(e)}'}, 500

    def delete(self, gig_id):
        """Delete gig by gig_id"""
        gig = Gig.query.filter_by(gig_id=gig_id).first()
        if not gig:
            return {'error': 'Gig not found'}, 404
        user = User.query.filter_by(uid=gig.provider_uid).first()
        if not user or not user.is_provider:
            return {'error': 'Only the provider can delete this gig'}, 403
        if GigInstance.query.filter_by(gig_id=gig_id).first():
            return {'error': 'Cannot delete gig with active instances'}, 400

        try:
            db.session.delete(gig)
            db.session.commit()
            return {'message': 'Gig deleted'}, 200
        except Exception as e:
            db.session.rollback()
            return {'error': f'Database error: {str(e)}'}, 500

@gigs_ns.route('/query')
class GigQuery(Resource):
    @gigs_ns.expect(query_gig_model)
    def post(self):
        """Query gigs by title, price, duration, status, or milestones"""
        data = gigs_ns.payload
        query = Gig.query

        if data.get('title'):
            query = query.filter(Gig.title.ilike(f"%{data['title']}%"))
        if data.get('price_min'):
            query = query.filter(Gig.price >= data['price_min'])
        if data.get('price_max'):
            query = query.filter(Gig.price <= data['price_max'])
        if data.get('duration_min'):
            query = query.filter(Gig.duration_hours >= data['duration_min'])
        if data.get('duration_max'):
            query = query.filter(Gig.duration_hours <= data['duration_max'])
        if data.get('status'):
            query = query.filter(Gig.status == data['status'])
        if data.get('has_milestones'):
            query = query.join(GigInstance).filter(GigInstance.milestones != [])

        gigs = query.all()
        if not gigs:
            return {'error': 'No gigs found'}, 404

        return [{
            'id': g.id,
            'gig_id': g.gig_id,
            'provider_uid': g.provider_uid,
            'title': g.title,
            'price': g.price,
            'duration_hours': g.duration_hours,
            'status': g.status,
            'created_at': g.created_at.isoformat(),
            'milestones': [gi.milestones for gi in GigInstance.query.filter_by(gig_id=g.gig_id).all()]
        } for g in gigs]