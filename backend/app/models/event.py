from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from ..core.database import Base

class Event(Base):
    __tablename__ = 'events'
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    date = Column(DateTime)
    location = Column(String(255))
    url = Column(String(500), unique=True, nullable=False, index=True)
    image_url = Column(String(500))
    source = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    scraped_at = Column(DateTime, default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<Event {self.title}>"


