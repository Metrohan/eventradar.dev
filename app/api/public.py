from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime, timezone
from ..core.database import get_db
from ..services.event_service import EventService
from ..services.announcement_service import AnnouncementService
from ..services.suggestion_service import SuggestionService
from ..services.event_request_service import EventRequestService
from ..services.source_catalog import get_enabled_sources
from ..schemas.event import EventResponse, EventListResponse
from ..schemas.announcement import AnnouncementResponse, AnnouncementListResponse
from ..schemas.suggestion import SuggestionCreate, SuggestionResponse
from ..schemas.event_request import EventRequestCreate, EventRequestResponse
from ..models.scraper_log import ScraperLog
from ..models.event import Event

router = APIRouter()


@router.get("/sources")
async def get_sources():
    """Return public metadata for enabled event-source integrations."""
    return [source.public_dict() for source in get_enabled_sources()]


@router.get("/events", response_model=EventListResponse)
async def get_events(
    active_only: bool = True,
    tags: Optional[List[str]] = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=100, ge=1, le=200),
    db: Session = Depends(get_db),
):
    event_service = EventService(db)

    try:
        offset = (page - 1) * page_size
        events = event_service.get_events(
            active_only=active_only,
            tags=tags,
            offset=offset,
            limit=page_size,
        )
        total_count = event_service.get_event_count(active_only=active_only, tags=tags)
        last_updated_event = event_service.get_last_updated_event()

        last_updated = None
        if last_updated_event:
            last_updated = last_updated_event.scraped_at.isoformat()

        return EventListResponse(
            events=events,  # type: ignore[arg-type]
            total_count=total_count,
            last_updated=last_updated,
            page=page,
            page_size=page_size,
            total_pages=(total_count + page_size - 1) // page_size,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading events: {str(e)}")


@router.get("/announcements", response_model=AnnouncementListResponse)
async def get_announcements(db: Session = Depends(get_db)):
    """
    Get all announcements (converted from Flask route /api/announcements)
    """
    announcement_service = AnnouncementService(db)

    try:
        announcements = announcement_service.get_announcements()
        return AnnouncementListResponse(
            announcements=announcements,  # type: ignore[arg-type]
            total_count=len(announcements),
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error loading announcements: {str(e)}"
        )


@router.get("/announcements/latest")
async def get_latest_announcement(db: Session = Depends(get_db)):
    """
    Get the latest announcement
    """
    announcement_service = AnnouncementService(db)

    try:
        announcement = announcement_service.get_latest_announcement()
        if not announcement:
            return None  # Frontend will handle null
        return announcement
    except Exception as e:
        return None  # Silently return null instead of 404


@router.get("/events/{event_id}", response_model=EventResponse)
async def get_event(event_id: int, db: Session = Depends(get_db)):
    event_service = EventService(db)
    event = event_service.get_event_by_id(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Etkinlik bulunamadı")
    return event


@router.get("/status")
async def get_status(db: Session = Depends(get_db)):
    """Platform sağlık durumu — scraper kayıtları, aktif etkinlik sayısı."""
    try:
        active_count = db.query(Event).filter(Event.is_active == True).count()
        total_count = db.query(Event).count()

        sources = db.query(ScraperLog.source).distinct().all()
        scrapers = []
        for (source,) in sources:
            latest: Optional[ScraperLog] = (
                db.query(ScraperLog)
                .filter(ScraperLog.source == source)
                .order_by(desc(ScraperLog.created_at))
                .first()
            )
            if latest:
                scrapers.append(
                    {
                        "source": latest.source,
                        "status": latest.status,
                        "events_found": latest.events_found,
                        "new_events": latest.new_events,
                        "duration_seconds": round(latest.duration_seconds or 0, 1),
                        "last_run": (
                            latest.created_at.isoformat() if latest.created_at else None
                        ),
                        "error": (
                            latest.error_message[:120] if latest.error_message else None
                        ),
                    }
                )

        scrapers.sort(key=lambda s: s["last_run"] or "", reverse=True)

        return {
            "active_events": active_count,
            "total_events": total_count,
            "scrapers": scrapers,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")


@router.post("/suggestions", response_model=SuggestionResponse)
async def submit_suggestion(
    suggestion: SuggestionCreate, db: Session = Depends(get_db)
):
    """
    Public endpoint to submit a suggestion/complaint (converted from /suggestions/oneri_sikayet)
    """
    suggestion_service = SuggestionService(db)
    try:
        new = suggestion_service.create_suggestion(suggestion)
        return new
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error creating suggestion: {str(e)}"
        )


@router.post("/event-requests", response_model=EventRequestResponse)
async def submit_event_request(
    request: EventRequestCreate, db: Session = Depends(get_db)
):
    """
    Public endpoint to submit an event request (converted from /requests/etkinlik-talep)
    """
    event_request_service = EventRequestService(db)
    try:
        new = event_request_service.create_event_request(request)
        return new
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error creating event request: {str(e)}"
        )
