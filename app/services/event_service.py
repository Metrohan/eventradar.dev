from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from datetime import datetime
from ..models.event import Event
from ..schemas.event import EventCreate, EventUpdate

class EventService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_events(self, active_only: bool = True) -> List[Event]:
        """Get all events, optionally filtered by active status"""
        query = self.db.query(Event)
        if active_only:
            query = query.filter(Event.is_active == True)
        return query.order_by(Event.date.desc()).all()
    
    def get_event_by_id(self, event_id: int) -> Optional[Event]:
        """Get event by ID"""
        return self.db.query(Event).filter(Event.id == event_id).first()
    
    def create_event(self, event_data: EventCreate) -> Event:
        """Create a new event"""
        try:
            db_event = Event(
                title=event_data.title,
                description=event_data.description,
                date=event_data.date,
                location=event_data.location,
                url=str(event_data.url),
                image_url=str(event_data.image_url) if event_data.image_url else None,
                source=event_data.source,
                is_active=event_data.is_active,
                scraped_at=datetime.now()
            )
            self.db.add(db_event)
            self.db.commit()
            self.db.refresh(db_event)
            return db_event
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Event with this URL already exists")
    
    def update_event(self, event_id: int, event_data: EventUpdate) -> Optional[Event]:
        """Update an existing event"""
        db_event = self.get_event_by_id(event_id)
        if not db_event:
            return None
        
        try:
            update_data = event_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                if field == "url" and value:
                    setattr(db_event, field, str(value))
                elif field == "image_url" and value:
                    setattr(db_event, field, str(value))
                else:
                    setattr(db_event, field, value)
            
            db_event.scraped_at = datetime.now()
            self.db.commit()
            self.db.refresh(db_event)
            return db_event
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Event with this URL already exists")
    
    def delete_event(self, event_id: int) -> bool:
        """Delete an event"""
        db_event = self.get_event_by_id(event_id)
        if not db_event:
            return False
        
        self.db.delete(db_event)
        self.db.commit()
        return True
    
    def get_total_active_events(self) -> int:
        """Get count of active events"""
        return self.db.query(Event).filter(Event.is_active == True).count()
    
    def get_last_updated_event(self) -> Optional[Event]:
        """Get the most recently updated event"""
        return self.db.query(Event).order_by(Event.scraped_at.desc()).first()


