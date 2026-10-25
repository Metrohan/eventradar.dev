from sqlalchemy import or_
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from datetime import datetime
from ..models.event import Event
from ..models.tag import Tag
from ..schemas.event import EventCreate, EventUpdate
from .date_extractor import extract_date_from_text
from .location_normalizer import normalize_location
from .event_lifecycle import history_event_filter, visible_event_filter
from ..utils.event_dates import local_now


class EventService:
    def __init__(self, db: Session):
        self.db = db

    def get_events(
        self,
        active_only: bool = True,
        tags: list[str] | None = None,
        offset: int = 0,
        limit: int | None = None,
        include_hidden: bool = True,
    ) -> List[Event]:
        """Get all events, optionally filtered by active status and/or tag names."""
        query = self.db.query(Event)
        if active_only:
            query = query.filter(*visible_event_filter())
        elif not include_hidden:
            query = query.filter(history_event_filter())
        if tags:
            query = query.filter(Event.tags.any(Tag.name.in_(tags)))
        query = query.order_by(Event.date.desc(), Event.id.desc()).offset(offset)
        if limit is not None:
            query = query.limit(limit)
        return query.all()

    def get_event_by_id(self, event_id: int) -> Optional[Event]:
        """Get event by ID"""
        return self.db.query(Event).filter(Event.id == event_id).first()

    def get_public_event_by_id(
        self, event_id: int, include_past: bool = False
    ) -> Optional[Event]:
        """Return only an event that is currently visible to public callers."""
        query = self.db.query(Event).filter(Event.id == event_id)
        if include_past:
            query = query.filter(history_event_filter())
        else:
            query = query.filter(*visible_event_filter())
        return query.first()

    def create_event(self, event_data: EventCreate) -> Event:
        """Create a new event"""
        try:
            # Eğer date yoksa açıklamadan çek
            date_val = event_data.date
            if not date_val and event_data.description:
                extracted = extract_date_from_text(event_data.description)
                if extracted:
                    date_val = extracted
            db_event = Event(
                title=event_data.title,
                description=event_data.description,
                date=date_val,
                application_deadline=event_data.application_deadline,
                location=normalize_location(event_data.location),
                url=str(event_data.url),
                image_url=str(event_data.image_url) if event_data.image_url else None,
                source=event_data.source,
                is_active=event_data.is_active,
                deactivation_reason=None if event_data.is_active else "manual",
                scraped_at=local_now(),
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
            update_data = event_data.model_dump(exclude_unset=True)
            if (
                "is_active" in update_data
                and update_data["is_active"] != db_event.is_active
            ):
                db_event.deactivation_reason = None if update_data["is_active"] else "manual"  # type: ignore[assignment]
            # Eğer date güncellenmiyorsa ve açıklama varsa, açıklamadan çek
            if (
                "date" not in update_data or not update_data.get("date")
            ) and update_data.get("description"):
                extracted = extract_date_from_text(update_data["description"])
                if extracted:
                    update_data["date"] = extracted
            for field, value in update_data.items():
                if field == "location":
                    setattr(db_event, field, normalize_location(value))
                elif field == "url" and value:
                    setattr(db_event, field, str(value))
                elif field == "image_url" and value:
                    setattr(db_event, field, str(value))
                else:
                    setattr(db_event, field, value)
            db_event.scraped_at = local_now()  # type: ignore[assignment]
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

    def get_total_active_events(self, tags: list[str] | None = None) -> int:
        """Get count of active events"""
        return self.get_event_count(active_only=True, tags=tags)

    def get_event_count(
        self,
        active_only: bool = True,
        tags: list[str] | None = None,
        include_hidden: bool = True,
    ) -> int:
        query = self.db.query(Event)
        if active_only:
            query = query.filter(*visible_event_filter())
        elif not include_hidden:
            query = query.filter(history_event_filter())
        if tags:
            query = query.filter(Event.tags.any(Tag.name.in_(tags)))
        return query.count()

    def get_last_updated_event(self) -> Optional[Event]:
        """Get the most recently updated event"""
        return self.db.query(Event).order_by(Event.scraped_at.desc()).first()
