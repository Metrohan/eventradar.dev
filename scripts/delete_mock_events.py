from app.core.database import SessionLocal
from app.models.event import Event

db = SessionLocal()
mock_events = db.query(Event).filter(Event.source == 'mock').all()
print(f"Found {len(mock_events)} mock events.")
for e in mock_events:
    print(f"Deleting: {e.title}")
    db.delete(e)

db.commit()
print("Mock events deleted.")
db.close()
