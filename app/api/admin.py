from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..core.database import get_db
from ..services.announcement_service import AnnouncementService
from ..services.suggestion_service import SuggestionService
from ..services.event_request_service import EventRequestService
from ..schemas.announcement import (
    AnnouncementCreate,
    AnnouncementResponse,
    AnnouncementListResponse,
)
from ..schemas.suggestion import SuggestionResponse, SuggestionListResponse
from ..schemas.event_request import EventRequestResponse, EventRequestListResponse
from ..schemas.scraper_log import ScraperLogResponse
from ..services.scraper_service import ScraperService
from ..schemas.subscriber import SubscriberResponse, BroadcastRequest
from ..services.notification_service import NotificationService
from ..core.auth import get_current_admin
from .admin_auth import router as auth_router
from .admin_events import router as events_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(events_router)


# Announcement management endpoints
@router.get("/announcements", response_model=AnnouncementListResponse)
async def get_admin_announcements(
    db: Session = Depends(get_db), current_admin: str = Depends(get_current_admin)
):
    """
    Get all announcements for admin
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


@router.post("/announcements", response_model=AnnouncementResponse)
async def create_announcement(
    announcement_data: AnnouncementCreate,
    db: Session = Depends(get_db),
    current_admin: str = Depends(get_current_admin),
):
    """
    Create a new announcement (converted from Flask route /announcements/add_announcement)
    """
    announcement_service = AnnouncementService(db)

    try:
        announcement = announcement_service.create_announcement(announcement_data)
        return announcement
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error creating announcement: {str(e)}"
        )


@router.delete("/announcements/{announcement_id}")
async def delete_announcement(
    announcement_id: int,
    db: Session = Depends(get_db),
    current_admin: str = Depends(get_current_admin),
):
    """
    Delete an announcement (converted from Flask route /announcements/delete_announcement/<int:announcement_id>)
    """
    announcement_service = AnnouncementService(db)

    try:
        success = announcement_service.delete_announcement(announcement_id)
        if not success:
            raise HTTPException(status_code=404, detail="Announcement not found")
        return {"message": "Announcement deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error deleting announcement: {str(e)}"
        )


# Suggestion management endpoints
@router.get("/suggestions", response_model=SuggestionListResponse)
async def get_suggestions(
    db: Session = Depends(get_db), current_admin: str = Depends(get_current_admin)
):
    """
    Get all suggestions (converted from Flask route /suggestions/suggestions)
    """
    suggestion_service = SuggestionService(db)

    try:
        suggestions = suggestion_service.get_suggestions()
        return SuggestionListResponse(
            suggestions=suggestions,  # type: ignore[arg-type]
            total_count=len(suggestions),
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error loading suggestions: {str(e)}"
        )


@router.delete("/suggestions/{suggestion_id}")
async def delete_suggestion(
    suggestion_id: int,
    db: Session = Depends(get_db),
    current_admin: str = Depends(get_current_admin),
):
    """
    Delete a suggestion
    """
    suggestion_service = SuggestionService(db)

    try:
        success = suggestion_service.delete_suggestion(suggestion_id)
        if not success:
            raise HTTPException(status_code=404, detail="Suggestion not found")
        return {"message": "Suggestion deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error deleting suggestion: {str(e)}"
        )


# Event request management endpoints
@router.get("/event-requests", response_model=EventRequestListResponse)
async def get_event_requests(
    db: Session = Depends(get_db), current_admin: str = Depends(get_current_admin)
):
    """
    Get all event requests (converted from Flask route /events/requests)
    """
    event_request_service = EventRequestService(db)

    try:
        requests = event_request_service.get_event_requests()
        return EventRequestListResponse(
            requests=requests,  # type: ignore[arg-type]
            total_count=len(requests),
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error loading event requests: {str(e)}"
        )


@router.delete("/event-requests/{request_id}")
async def delete_event_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_admin: str = Depends(get_current_admin),
):
    """
    Delete an event request
    """
    event_request_service = EventRequestService(db)

    try:
        success = event_request_service.delete_event_request(request_id)
        if not success:
            raise HTTPException(status_code=404, detail="Event request not found")
        return {"message": "Event request deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error deleting event request: {str(e)}"
        )


# Scraper Control Center endpoints
@router.get("/scrapers/logs", response_model=List[ScraperLogResponse])
async def get_scraper_logs(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_admin: str = Depends(get_current_admin),
):
    """Get scraper execution logs"""
    print(f"DEBUG: get_scraper_logs called by {current_admin}")
    service = ScraperService(db)
    return service.get_logs(limit)


@router.get("/scrapers/status", response_model=List[ScraperLogResponse])
async def get_scraper_status(
    db: Session = Depends(get_db), current_admin: str = Depends(get_current_admin)
):
    """Get latest status for each scraper source"""
    service = ScraperService(db)
    return service.get_latest_status()


@router.post("/scrapers/trigger")
async def trigger_scraper(
    source: str = "all",
    db: Session = Depends(get_db),
    current_admin: str = Depends(get_current_admin),
):
    """Trigger a scraper manually"""
    service = ScraperService(db)
    return service.trigger_scraper(source)


# Notification Management endpoints
@router.get("/notifications/stats")
async def get_notification_stats(
    db: Session = Depends(get_db), current_admin: str = Depends(get_current_admin)
):
    """Get subscriber statistics"""
    service = NotificationService(db)
    return service.get_stats()


@router.get("/notifications/subscribers", response_model=List[SubscriberResponse])
async def get_subscribers(
    db: Session = Depends(get_db), current_admin: str = Depends(get_current_admin)
):
    """Get all subscribers"""
    service = NotificationService(db)
    return service.get_subscribers()


@router.post("/notifications/broadcast")
async def broadcast_message(
    request: BroadcastRequest,
    db: Session = Depends(get_db),
    current_admin: str = Depends(get_current_admin),
):
    """Broadcast a message"""
    service = NotificationService(db)
    return service.broadcast_message(request)


# Analytics endpoints
from ..services.analytics_service import AnalyticsService


@router.get("/analytics/traffic")
async def get_traffic_stats(
    days: int = 30,
    db: Session = Depends(get_db),
    current_admin: str = Depends(get_current_admin),
):
    """Get site traffic statistics"""
    service = AnalyticsService(db)
    return service.get_stats(days)


@router.get("/quality")
async def get_data_quality(
    db: Session = Depends(get_db),
    current_admin: str = Depends(get_current_admin),
):
    """Data quality dashboard — source health and event completeness."""
    from ..models.event import Event
    from ..services.source_quality import SourceQuality

    total_events = db.query(Event).count()
    active_events = db.query(Event).filter(Event.is_active == True).count()

    return {
        "total_events": total_events,
        "active_events": active_events,
        "sources": SourceQuality(db).get_metrics(),
    }
