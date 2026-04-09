from datetime import datetime
from extensions import db

class Suggestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    suggestion_type = db.Column(db.String(50))
    suggestion_text = db.Column(db.Text)
    suggestion_title = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
