from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, validates
from ..core.database import Base
from ..utils.event_urls import new_event_slug
from ..utils.location import parse_location


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(160), unique=True, nullable=False, default=new_event_slug)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    date = Column(DateTime)
    application_deadline = Column(DateTime)
    location = Column(Text)
    # Derived from ``location`` (see the validator below); NULL when unknown.
    city = Column(String(64), nullable=True)
    attendance = Column(String(16), nullable=True)  # online / in_person / hybrid
    venue = Column(Text, nullable=True)
    url = Column(String(500), unique=True, nullable=False, index=True)
    image_url = Column(String(500))
    thumbnail_url = Column(String(500))
    source = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    deactivation_reason = Column(String(16), nullable=True)
    scraped_at = Column(DateTime, default=func.now(), nullable=False)
    last_seen_at = Column(DateTime, default=func.now(), nullable=False, index=True)
    tags = relationship("Tag", secondary="event_tags", lazy="selectin")

    @validates("location")
    def _derive_location_fields(self, _key, value):
        # Runs on every assignment, including an unchanged one, so each scrape
        # refreshes the derived fields of the rows it touches.
        info = parse_location(value)
        self.city = info.city
        self.attendance = info.attendance
        self.venue = info.venue
        return value

    def __repr__(self):
        return f"<Event {self.title}>"
