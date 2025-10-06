from flask import current_app
from flask_restx import Namespace, Resource, fields
from app.db import db
from app.models import Review, Gig, User
from web3 import Web3
from datetime import datetime

reviews_ns = Namespace('reviews', description='Review operations')

review_model = reviews_ns.model('Review', {
    'gig_id': fields.String(required=True),
    'reviewer_uid': fields.String(required=True),
    'rating': fields.Integer(required=True),
    'comment': fields.String,
    'completion_status': fields.String(enum=['completed', 'disputed'], default='pending'),
    'signed_tx': fields.String  
})

@reviews_ns.route('')
class Reviews(Resource):
    @reviews_ns.expect(review_model)
    def post(self):
        data = reviews_ns.payload
        gig = Gig.query.filter_by(gig_id=data['gig_id']).first()
        if not gig:
            return {"error": "Gig not found"}, 404
        user = User.query.filter_by(uid=data['reviewer_uid']).first()
        if not user:
            return {"error": f"User not found for UID {data['reviewer_uid']}"}, 404
        if user.role not in ['hirer', 'both']:
            return {"error": "Only hirers can submit reviews"}, 403

        try:
            review = Review.create_review(
                gig_id=data['gig_id'],
                reviewer_uid=data['reviewer_uid'],
                rating=data['rating'],
                comment=data.get('comment'),
                completion_status=data.get('completion_status', 'pending')
            )
            if review['completion_status'] == 'completed':
                signed_tx = data.get('signed_tx')
                if not signed_tx:
                    return {"error": "signed_tx required for completed status"}, 400

                w3 = Web3(Web3.HTTPProvider(current_app.config['BASE_RPC_URL']))
                try:
                    tx_hash = w3.eth.send_raw_transaction(signed_tx)
                    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
                    if receipt.status != 1:
                        return {"error": "Transaction failed"}, 400
                except Exception as e:
                    db.session.rollback()
                    return {"error": f"Failed to approve gig: {str(e)}"}, 400

                return {
                    "message": "Review created, gig approved",
                    "id": review['id'],
                    "tx_hash": tx_hash.hex()
                }, 201
            elif review['completion_status'] == 'disputed':
                return {
                    "message": "Review created, dispute process initiated",
                    "id": review['id']
                }, 201
            return {"message": "Review created", "id": review['id']}, 201
        except Exception as e:
            db.session.rollback()
            return {"error": f"Database error: {str(e)}"}, 500

    def get(self):
        reviews = Review.query.all()
        return [{
            'id': r.id,
            'gig_id': r.gig_id,
            'reviewer_uid': r.reviewer_uid,
            'rating': r.rating,
            'comment': r.comment,
            'completion_status': r.completion_status,
            'created_at': r.created_at.isoformat()
        } for r in reviews]