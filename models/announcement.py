from datetime import datetime
from extensions import db

class Announcement(db.Model):
    __tablename__ = 'announcements'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

    def __repr__(self):
        return f"<Announcement {self.title}>"
