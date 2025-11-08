from sqlalchemy import Column, Integer, String, Text, Date, DateTime
from sqlalchemy.sql import func
from ..core.database import Base

class EventRequest(Base):
    __tablename__ = 'event_requests'
    
    id = Column(Integer, primary_key=True, index=True)
    event_link = Column(String(500), nullable=False)
    event_title = Column(String(300), nullable=False)
    event_date = Column(Date, nullable=True)
    event_description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<EventRequest {self.event_title}>"


