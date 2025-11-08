from sqlalchemy.orm import Session
from typing import List, Optional
from ..models.event_request import EventRequest
from ..schemas.event_request import EventRequestCreate

class EventRequestService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_event_requests(self) -> List[EventRequest]:
        """Get all event requests ordered by creation date"""
        return self.db.query(EventRequest).order_by(EventRequest.created_at.desc()).all()
    
    def get_event_request_by_id(self, request_id: int) -> Optional[EventRequest]:
        """Get event request by ID"""
        return self.db.query(EventRequest).filter(EventRequest.id == request_id).first()
    
    def create_event_request(self, request_data: EventRequestCreate) -> EventRequest:
        """Create a new event request"""
        db_request = EventRequest(
            event_link=str(request_data.event_link),
            event_title=request_data.event_title,
            event_date=request_data.event_date,
            event_description=request_data.event_description
        )
        self.db.add(db_request)
        self.db.commit()
        self.db.refresh(db_request)
        return db_request
    
    def delete_event_request(self, request_id: int) -> bool:
        """Delete an event request"""
        db_request = self.get_event_request_by_id(request_id)
        if not db_request:
            return False
        
        self.db.delete(db_request)
        self.db.commit()
        return True


