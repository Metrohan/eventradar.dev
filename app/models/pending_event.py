from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from ..core.database import Base

class PendingEvent(Base):
    __tablename__ = 'pending_events'
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    date = Column(DateTime)
    location = Column(String(255))
    url = Column(String(500), nullable=False)
    image_url = Column(String(500))
    source = Column(String(100), nullable=False)
    scraped_at = Column(DateTime, default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<PendingEvent {self.title}>"


