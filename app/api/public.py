from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..core.database import get_db
from ..services.event_service import EventService
from ..services.announcement_service import AnnouncementService
from ..services.suggestion_service import SuggestionService
from ..services.event_request_service import EventRequestService
from ..schemas.event import EventResponse, EventListResponse
from ..schemas.announcement import AnnouncementResponse, AnnouncementListResponse
from ..schemas.suggestion import SuggestionCreate, SuggestionResponse
from ..schemas.event_request import EventRequestCreate, EventRequestResponse

router = APIRouter()


@router.get("/events", response_model=EventListResponse)
async def get_events(
    active_only: bool = True,
    tags: Optional[List[str]] = Query(default=None),
    db: Session = Depends(get_db),
):
    event_service = EventService(db)

    try:
        events = event_service.get_events(active_only=active_only, tags=tags)
        total_count = event_service.get_total_active_events()
        last_updated_event = event_service.get_last_updated_event()

        last_updated = None
        if last_updated_event:
            last_updated = last_updated_event.scraped_at.isoformat()

        return EventListResponse(
            events=events,  # type: ignore[arg-type]
            total_count=total_count,
            last_updated=last_updated,
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


@router.post("/suggestions", response_model=SuggestionResponse)
async def submit_suggestion(
    suggestion: SuggestionCreate, db: Session = Depends(get_db)
):
    """
    Public endpoint to submit a suggestion/complaint (converted from /suggestions/oneri_sikayet)
    """
    suggestion_service = SuggestionService(db)
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
