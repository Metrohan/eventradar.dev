from datetime import datetime
from extensions import db

class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.DateTime)
    location = db.Column(db.String(255))
    url = db.Column(db.String(500), unique=True, nullable=False)
    image_url = db.Column(db.String(500))
    source = db.Column(db.String(100), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    scraped_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

    def __repr__(self):
        return f"<Event {self.title}>"
