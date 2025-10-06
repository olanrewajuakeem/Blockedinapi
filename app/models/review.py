from app.db import db
from datetime import datetime

class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    gig_id = db.Column(db.String(255), nullable=False)
    reviewer_uid = db.Column(db.String(255), nullable=False)  
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    completion_status = db.Column(db.String(50), default='pending')  
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @staticmethod
    def create_review(gig_id, reviewer_uid, rating, comment=None, completion_status='pending'):
        review = Review(
            gig_id=gig_id,
            reviewer_uid=reviewer_uid,
            rating=rating,
            comment=comment,
            completion_status=completion_status
        )
        db.session.add(review)
        db.session.commit()
        return {
            'id': review.id,
            'gig_id': review.gig_id,
            'reviewer_uid': review.reviewer_uid,
            'rating': review.rating,
            'comment': review.comment,
            'completion_status': review.completion_status,
            'created_at': review.created_at.isoformat()
        }