from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base
from ..utils.event_urls import new_event_slug


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(160), unique=True, nullable=False, default=new_event_slug)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    date = Column(DateTime)
    application_deadline = Column(DateTime)
    location = Column(Text)
    url = Column(String(500), unique=True, nullable=False, index=True)
    image_url = Column(String(500))
    thumbnail_url = Column(String(500))
    source = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    deactivation_reason = Column(String(16), nullable=True)
    scraped_at = Column(DateTime, default=func.now(), nullable=False)
    last_seen_at = Column(DateTime, default=func.now(), nullable=False, index=True)
    tags = relationship("Tag", secondary="event_tags", lazy="selectin")

    def __repr__(self):
        return f"<Event {self.title}>"
