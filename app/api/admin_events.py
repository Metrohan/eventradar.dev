import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..core.auth import get_current_admin
from ..core.database import get_db
from ..schemas.event import EventCreate, EventListResponse, EventResponse, EventUpdate
from ..services.event_service import EventService

logger = logging.getLogger(__name__)

router = APIRouter()


def _announce(db: Session, event) -> None:
    """Announce a hand-added event like a scraped one (Telegram + push).

    Runs after the commit and never fails the request. Inactive events and
    ones without technical relevance are not announced.
    """
    from ..services import push_service, telegram_service
    from ..utils.topic_policy import announceable

    if not event.is_active:
        return
    payload = {
        "title": event.title,
        "url": event.url,
        "source": event.source,
        "description": event.description or "",
        "date": event.date.strftime("%Y-%m-%d %H:%M:%S") if event.date else "",
        "location": event.location,
    }
    try:
        events = announceable([payload])
        if not events:
            return
        telegram_service.notify_new_events(events)
        push_service.notify_new_events(db, events)
    except Exception:
        logger.exception("Event announcement failed")


@router.get("/events", response_model=EventListResponse)
async def get_admin_events(
    db: Session = Depends(get_db), current_admin: str = Depends(get_current_admin)
):
    event_service = EventService(db)
    try:
        events = event_service.get_events(active_only=False)
        last_updated_event = event_service.get_last_updated_event()
        last_updated = (
            last_updated_event.scraped_at.isoformat() if last_updated_event else None
        )
        return EventListResponse(
            events=events,  # type: ignore[arg-type]
            total_count=len(events),
            last_updated=last_updated,
        )
    except Exception as exc:
        logger.exception("Admin request failed")
        raise HTTPException(status_code=500, detail="Error loading events")


@router.post("/events", response_model=EventResponse)
async def create_event(
    event_data: EventCreate,
    db: Session = Depends(get_db),
    current_admin: str = Depends(get_current_admin),
):
    try:
        event = EventService(db).create_event(event_data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("Admin request failed")
        raise HTTPException(status_code=500, detail="Error creating event")
    _announce(db, event)
    return event


@router.put("/events/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: int,
    event_data: EventUpdate,
    db: Session = Depends(get_db),
    current_admin: str = Depends(get_current_admin),
):
    try:
        event = EventService(db).update_event(event_id, event_data)
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        return event
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Admin request failed")
        raise HTTPException(status_code=500, detail="Error updating event")


@router.delete("/events/{event_id}")
async def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_admin: str = Depends(get_current_admin),
):
    try:
        if not EventService(db).delete_event(event_id):
            raise HTTPException(status_code=404, detail="Event not found")
        return {"message": "Event deleted successfully"}
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Admin request failed")
        raise HTTPException(status_code=500, detail="Error deleting event")
