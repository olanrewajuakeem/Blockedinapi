from app.db import db
from datetime import datetime

class GigInstance(db.Model):
    __tablename__ = 'gig_instances'
    id = db.Column(db.Integer, primary_key=True)
    gig_id = db.Column(db.String(255), nullable=False)
    hirer_wallet = db.Column(db.String(42), nullable=False)
    escrow_address = db.Column(db.String(42), nullable=False)
    status = db.Column(db.String(50), default='funded')
    milestones = db.Column(db.JSON, default=[])
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @staticmethod
    def create_gig_instance(gig_id, hirer_wallet, escrow_address, status='funded', milestones=None):
        instance = GigInstance(
            gig_id=gig_id,
            hirer_wallet=hirer_wallet,
            escrow_address=escrow_address,
            status=status,
            milestones=milestones or []
        )
        db.session.add(instance)
        db.session.commit()
        return {
            'id': instance.id,
            'gig_id': instance.gig_id,
            'hirer_wallet': instance.hirer_wallet,
            'escrow_address': instance.escrow_address,
            'status': instance.status,
            'milestones': instance.milestones,
            'created_at': instance.created_at.isoformat()
        }

    @staticmethod
    def get_gig_instance(gig_id, hirer_wallet):
        instance = GigInstance.query.filter_by(gig_id=gig_id, hirer_wallet=hirer_wallet).first()
        if instance:
            return {
                'id': instance.id,
                'gig_id': instance.gig_id,
                'hirer_wallet': instance.hirer_wallet,
                'escrow_address': instance.escrow_address,
                'status': instance.status,
                'milestones': instance.milestones,
                'created_at': instance.created_at.isoformat()
            }
        return None

    @staticmethod
    def update_gig_instance(gig_id, hirer_wallet, updates):
        instance = GigInstance.query.filter_by(gig_id=gig_id, hirer_wallet=hirer_wallet).first()
        if instance:
            for key, value in updates.items():
                setattr(instance, key, value)
            db.session.commit()
            return {
                'id': instance.id,
                'gig_id': instance.gig_id,
                'hirer_wallet': instance.hirer_wallet,
                'escrow_address': instance.escrow_address,
                'status': instance.status,
                'milestones': instance.milestones,
                'created_at': instance.created_at.isoformat()
            }
        return None