from datetime import datetime
from extensions import db

class SimilarEventPair(db.Model):
    __tablename__ = 'similar_event_pairs'
    id = db.Column(db.Integer, primary_key=True)
    pending_event_id = db.Column(db.Integer, db.ForeignKey('pending_events.id'), nullable=False)
    existing_event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    similarity_score = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

    pending_event = db.relationship('PendingEvent', backref=db.backref('similar_pairs', lazy=True))
    existing_event = db.relationship('Event', backref=db.backref('similar_pairs', lazy=True))

    def __repr__(self):
        return f"<SimilarEventPair {self.pending_event.title} - {self.existing_event.title}>"
