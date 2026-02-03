from app.core.database import SessionLocal
from app.models.event import Event

db = SessionLocal()
events = db.query(Event).all()
print(f"Total events: {len(events)}")
for e in events:
    print(f"ID: {e.id}, Title: {e.title}, Source: {e.source}")
db.close()
