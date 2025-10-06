from flask_restx import Namespace, Resource, fields
from app.models import Gig
from app.db import db
from datetime import datetime

gigs_ns = Namespace('gigs', description='Gig operations')

gig_model = gigs_ns.model('Gig', {
    'gig_id': fields.String(required=False, description='Unique gig identifier (optional, auto-generated if not provided)'),
    'provider_uid': fields.String(required=True),
    'title': fields.String(required=True),
    'price': fields.Float(required=True),
    'duration_hours': fields.Integer(required=True)
})

@gigs_ns.route('')
class Gigs(Resource):
    @gigs_ns.expect(gig_model)
    def post(self):
        data = gigs_ns.payload
        gig_id = data.get('gig_id')
        if gig_id and Gig.query.filter_by(gig_id=gig_id).first():
            return {'error': 'Gig ID already exists'}, 400

        try:
            gig = Gig(
                gig_id=gig_id,  
                provider_uid=data['provider_uid'],
                title=data['title'],
                price=data['price'],
                duration_hours=data['duration_hours'],
                status='pending',
                created_at=datetime.utcnow()
            )
            db.session.add(gig)
            db.session.commit()
            return {'gig_id': gig.gig_id}, 201
        except Exception as e:
            db.session.rollback()
            return {'error': f'Database error: {str(e)}'}, 500

    def get(self):
        gigs = Gig.query.all()
        return [{'gig_id': g.gig_id, 'title': g.title, 'price': g.price} for g in gigs]