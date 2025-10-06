from flask import request
from flask_restx import Namespace, Resource, fields
from app.db import db

deliverables_ns = Namespace('deliverables', description='Deliverable operations')

deliverable_model = deliverables_ns.model('Deliverable', {
    'gig_id': fields.String(required=True),
    'content': fields.String(required=True)
})

@deliverables_ns.route('')
class Deliverables(Resource):
    @deliverables_ns.expect(deliverable_model)
    def post(self):
        data = deliverables_ns.payload
        deliverable = {'gig_id': data['gig_id'], 'content': data['content']}
        db.deliverables.insert_one(deliverable)
        return {"message": "Deliverable submitted"}, 201