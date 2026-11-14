from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Boolean,
    ForeignKey,
    event,
    inspect,
    select,
    insert,
    update,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, validates
from ..core.database import Base
from ..utils.event_urls import new_event_slug
from ..utils.location import parse_location


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(160), unique=True, nullable=False, default=new_event_slug)
    slug_version = Column(Integer, nullable=False, default=2, server_default="1")
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


class EventSlugAlias(Base):
    __tablename__ = "event_slug_aliases"

    slug = Column(String(160), primary_key=True)
    # Nullable only during a new Event INSERT's default evaluation. Linked by
    # the mapper hook before the transaction can commit.
    event_id = Column(
        Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=True, index=True
    )


def _reserve_route(_mapper, connection, target):
    table = EventSlugAlias.__table__
    row = connection.execute(
        select(table.c.event_id).where(table.c.slug == target.slug)
    ).first()
    if row is None:
        connection.execute(insert(table).values(slug=target.slug, event_id=target.id))
    elif row.event_id is None:
        connection.execute(
            update(table).where(table.c.slug == target.slug).values(event_id=target.id)
        )
    elif row.event_id != target.id:
        # Raise a real uniqueness error so callers roll back the whole insert.
        connection.execute(insert(table).values(slug=target.slug, event_id=target.id))


def _reserve_updated_route(mapper, connection, target):
    if inspect(target).attrs.slug.history.has_changes():
        _reserve_route(mapper, connection, target)


event.listen(Event, "after_insert", _reserve_route)
event.listen(Event, "after_update", _reserve_updated_route)
