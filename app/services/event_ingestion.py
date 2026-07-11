from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, cast

from sqlalchemy.orm import Session

from ..models.event import Event
from ..models.tag import Tag
from .date_extractor import parse_event_date
from .tag_service import classify_event

SessionFactory = Callable[[], Session]
NotificationAdapter = Callable[[list[dict[str, Any]]], None]
Clock = Callable[[], datetime]


class IngestionError(RuntimeError):
    """Raised when an ingestion transaction cannot be completed."""


@dataclass(frozen=True)
class ScrapedEvent:
    title: str | None
    url: str | None
    source: str
    description: str | None = None
    date: datetime | str | None = None
    application_deadline: datetime | str | None = None
    location: str | None = None
    image_url: str | None = None

    @classmethod
    def from_mapping(
        cls, payload: Mapping[str, Any], default_source: str
    ) -> "ScrapedEvent":
        return cls(
            title=payload.get("title"),
            url=payload.get("url"),
            source=payload.get("source") or default_source,
            description=payload.get("description"),
            date=payload.get("date"),
            application_deadline=payload.get("application_deadline"),
            location=payload.get("location"),
            image_url=payload.get("image_url"),
        )

    def notification_payload(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "url": self.url,
            "source": self.source,
            "description": self.description,
            "date": self.date,
            "application_deadline": self.application_deadline,
            "location": self.location,
            "image_url": self.image_url,
        }


@dataclass
class IngestionResult:
    new: int = 0
    updated: int = 0
    failed_urls: list[str] = field(default_factory=list)
    notification_error: str | None = None

    @property
    def failed(self) -> int:
        return len(self.failed_urls)

    def summary(self) -> str:
        value = f"New: {self.new}, Updated: {self.updated}"
        if self.failed:
            value += f", Failed: {self.failed}"
        return value


def normalize_date(value: datetime | str | None) -> datetime | None:
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    if value.strip().casefold() in {"tarih belirtilmemiş", "belirtilmemiş", "-", ""}:
        return None
    return parse_event_date(value)


class EventIngestion:
    """Persist canonical scraped events and enforce their lifecycle policy."""

    def __init__(
        self,
        session_factory: SessionFactory,
        notification_adapter: NotificationAdapter | None = None,
        clock: Clock = datetime.now,
    ):
        self._session_factory = session_factory
        self._notification_adapter = notification_adapter
        self._clock = clock

    def ingest(self, events: Iterable[ScrapedEvent]) -> IngestionResult:
        items = list(events)
        result = IngestionResult()
        db = self._session_factory()
        new_events: list[ScrapedEvent] = []

        try:
            urls = [item.url for item in items if item.url]
            existing_map: dict[str, Event] = {
                cast(str, event.url): event
                for event in db.query(Event).filter(Event.url.in_(urls)).all()
            }
            all_tags: dict[str, Tag] = {
                str(tag.name): tag for tag in db.query(Tag).all()
            }
            now = self._clock()
            seen_urls: set[str] = set()

            for item in items:
                if not item.url or item.url in seen_urls:
                    continue
                seen_urls.add(item.url)

                try:
                    is_new = False
                    with db.begin_nested():
                        date_value = normalize_date(item.date)
                        deadline_value = normalize_date(item.application_deadline)
                        existing = existing_map.get(item.url)

                        if existing:
                            self._update_event(
                                existing,
                                item,
                                date_value,
                                deadline_value,
                                now,
                                all_tags,
                            )
                        else:
                            self._create_event(
                                db, item, date_value, deadline_value, now, all_tags
                            )
                            is_new = True

                    if is_new:
                        result.new += 1
                        new_events.append(item)
                    else:
                        result.updated += 1
                except Exception:
                    result.failed_urls.append(item.url)

            db.commit()
        except Exception as exc:
            db.rollback()
            raise IngestionError(str(exc)) from exc
        finally:
            db.close()

        if new_events and self._notification_adapter:
            try:
                self._notification_adapter(
                    [event.notification_payload() for event in new_events]
                )
            except Exception as exc:
                result.notification_error = str(exc)

        return result

    def deactivate_past(self) -> int:
        db = self._session_factory()
        try:
            past_events = (
                db.query(Event)
                .filter(Event.is_active == True, Event.date < self._clock())
                .all()
            )
            for event in past_events:
                event.is_active = False  # type: ignore[assignment]
            db.commit()
            return len(past_events)
        except Exception as exc:
            db.rollback()
            raise IngestionError(str(exc)) from exc
        finally:
            db.close()

    def reconcile_source(
        self, source: str, grace_period: timedelta = timedelta(days=3)
    ) -> int:
        """Deactivate source events not observed within the grace period."""
        db = self._session_factory()
        cutoff = self._clock() - grace_period
        try:
            stale_events = (
                db.query(Event)
                .filter(
                    Event.source == source,
                    Event.is_active == True,
                    Event.last_seen_at < cutoff,
                )
                .all()
            )
            for event in stale_events:
                event.is_active = False  # type: ignore[assignment]
            db.commit()
            return len(stale_events)
        except Exception as exc:
            db.rollback()
            raise IngestionError(str(exc)) from exc
        finally:
            db.close()

    @staticmethod
    def _update_event(
        event: Event,
        item: ScrapedEvent,
        date_value: datetime | None,
        deadline_value: datetime | None,
        now: datetime,
        all_tags: dict[str, Tag],
    ) -> None:
        event.title = item.title or cast(str, event.title)  # type: ignore[assignment]
        event.description = item.description or cast(  # type: ignore[assignment]
            str | None, event.description
        )
        if date_value is not None:
            event.date = date_value  # type: ignore[assignment]
        effective_date = date_value or cast(datetime | None, event.date)
        if effective_date is not None and effective_date < now:
            event.is_active = False  # type: ignore[assignment]
        if deadline_value is not None:
            event.application_deadline = deadline_value  # type: ignore[assignment]
        event.location = item.location or cast(  # type: ignore[assignment]
            str | None, event.location
        )
        event.image_url = item.image_url or cast(  # type: ignore[assignment]
            str | None, event.image_url
        )
        event.scraped_at = now  # type: ignore[assignment]
        event.last_seen_at = now  # type: ignore[assignment]
        tag_names = classify_event(
            item.title or cast(str, event.title), item.description
        )
        event.tags = [all_tags[name] for name in tag_names if name in all_tags]

    @staticmethod
    def _create_event(
        db: Session,
        item: ScrapedEvent,
        date_value: datetime | None,
        deadline_value: datetime | None,
        now: datetime,
        all_tags: dict[str, Tag],
    ) -> None:
        event = Event(
            title=item.title,
            description=item.description,
            date=date_value,
            application_deadline=deadline_value,
            location=item.location,
            url=item.url,
            image_url=item.image_url,
            source=item.source,
            is_active=date_value is None or date_value >= now,
            scraped_at=now,
            last_seen_at=now,
        )
        db.add(event)
        db.flush()
        tag_names = classify_event(item.title or "", item.description)
        event.tags = [all_tags[name] for name in tag_names if name in all_tags]


def build_event_ingestion() -> EventIngestion:
    from ..core.database import SessionLocal
    from .telegram_service import notify_new_events

    return EventIngestion(SessionLocal, notify_new_events)
