import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.event import Event
from app.core.config import settings
from app.core.database import Base

def create_mock_events():
    # Use the database URL from settings
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        # Check if events likely exist
        if db.query(Event).count() > 0:
            print("Events likely already exist. Skipping mock data generation.")
            return

        print("Adding mock events...")
        
        events = [
            Event(
                title="Tech Innovations Summit 2026",
                description="A global summit discussing the future of AI and robotics.",
                date=datetime.now() + timedelta(days=30),
                location="Istanbul, Turkey",
                url="https://example.com/tech-summit-2026",
                image_url="https://images.unsplash.com/photo-1540575467063-178a50c2df87?auto=format&fit=crop&w=1000&q=80",
                source="mock",
                is_active=True
            ),
            Event(
                title="Developer Week Eurasia",
                description="Largest developer conference in the region.",
                date=datetime.now() + timedelta(days=60),
                location="Online",
                url="https://example.com/dev-week",
                image_url="https://images.unsplash.com/photo-1591115765373-5207764f72e7?auto=format&fit=crop&w=1000&q=80",
                source="mock",
                is_active=True
            ),
             Event(
                title="Startup Grind Global",
                description="Connecting startups with investors.",
                date=datetime.now() + timedelta(days=15),
                location="Silicon Valley, USA",
                url="https://example.com/startup-grind",
                image_url="https://images.unsplash.com/photo-1475721027767-4d529c148373?auto=format&fit=crop&w=1000&q=80",
                source="mock",
                is_active=True
            ),
            Event(
                title="React Native EU",
                description="Focusing on React Native development.",
                date=datetime.now() + timedelta(days=120),
                location="Wroclaw, Poland",
                url="https://example.com/react-native-eu",
                image_url="https://images.unsplash.com/photo-1505373877841-8d25f7d46678?auto=format&fit=crop&w=1000&q=80",
                source="mock",
                is_active=True
            )
        ]

        db.add_all(events)
        db.commit()
        print(f"Successfully added {len(events)} mock events.")

    except Exception as e:
        print(f"Error adding mock events: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_mock_events()
