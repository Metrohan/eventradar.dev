from datetime import datetime
from extensions import db

class EventRequest(db.Model):
    __tablename__ = 'event_requests'
    id = db.Column(db.Integer, primary_key=True)
    event_link = db.Column(db.String(500), nullable=False)
    event_title = db.Column(db.String(300), nullable=False)
    event_date = db.Column(db.Date, nullable=True)
    event_description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

    def __repr__(self):
        return f"<EventRequest {self.event_title}>"
