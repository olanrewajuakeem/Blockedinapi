from flask import current_app
from flask_restx import Namespace, Resource, fields
from app.db import db
from app.models import Dispute, Gig, User, Escrow
from datetime import datetime

disputes_ns = Namespace('disputes', description='Dispute operations')

dispute_model = disputes_ns.model('Dispute', {
    'gig_id': fields.String(required=True),
    'initiator_uid': fields.String(required=True),
    'reason': fields.String(required=True)
})

resolve_model = disputes_ns.model('ResolveDispute', {
    'gig_id': fields.String(required=True),
    'resolution': fields.String(required=True),
    'outcome': fields.String(enum=['provider', 'hirer'], required=True)
})

@disputes_ns.route('')
class Disputes(Resource):
    @disputes_ns.expect(dispute_model)
    def post(self):
        data = disputes_ns.payload
        gig = Gig.query.filter_by(gig_id=data['gig_id']).first()
        if not gig:
            return {"error": "Gig not found"}, 404
        user = User.query.filter_by(uid=data['initiator_uid']).first()
        if not user:
            return {"error": f"User not found for UID {data['initiator_uid']}"}, 404
        if user.role not in ['hirer', 'provider', 'both']:
            return {"error": "Only hirers or providers can file disputes"}, 403
        escrow = Escrow.query.filter_by(gig_id=data['gig_id']).first()
        if not escrow:
            return {"error": "Escrow not funded for this gig"}, 400

        try:
            dispute = Dispute(
                gig_id=data['gig_id'],
                initiator_uid=data['initiator_uid'],
                reason=data['reason'],
                status='pending',  # Align with reviews
                created_at=datetime.utcnow()
            )
            db.session.add(dispute)
            db.session.commit()
            return {
                "message": "Dispute created",
                "id": dispute.id,
                "gig_id": dispute.gig_id,
                "initiator_uid": dispute.initiator_uid,
                "reason": dispute.reason
            }, 201
        except Exception as e:
            db.session.rollback()
            return {"error": f"Database error: {str(e)}"}, 500

    def get(self):
        disputes = Dispute.query.all()
        return [{
            'id': d.id,
            'gig_id': d.gig_id,
            'initiator_uid': d.initiator_uid,
            'reason': d.reason,
            'status': d.status,
            'outcome': d.outcome,
            'created_at': d.created_at.isoformat()
        } for d in disputes]

@disputes_ns.route('/resolve')
class ResolveDispute(Resource):
    @disputes_ns.expect(resolve_model)
    def post(self):
        data = disputes_ns.payload
        dispute = Dispute.query.filter_by(gig_id=data['gig_id']).first()
        if not dispute:
            return {"error": "Dispute not found"}, 404

        try:
            dispute.resolution = data['resolution']
            dispute.status = 'resolved'
            dispute.outcome = data['outcome']
            db.session.commit()
            return {
                "message": "Dispute resolved",
                "id": dispute.id,
                "gig_id": dispute.gig_id,
                "outcome": dispute.outcome
            }, 200
        except Exception as e:
            db.session.rollback()
            return {"error": f"Database error: {str(e)}"}, 500