from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..core.database import get_db
from ..services.event_service import EventService
from ..services.announcement_service import AnnouncementService
from ..schemas.event import EventResponse, EventListResponse
from ..schemas.announcement import AnnouncementResponse, AnnouncementListResponse

router = APIRouter()

@router.get("/events", response_model=EventListResponse)
async def get_events(
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """
    Get all events (converted from Flask route /events)
    """
    event_service = EventService(db)
    announcement_service = AnnouncementService(db)
    
    try:
        events = event_service.get_events(active_only=active_only)
        total_count = event_service.get_total_active_events()
        last_updated_event = event_service.get_last_updated_event()
        
        last_updated = None
        if last_updated_event:
            last_updated = last_updated_event.scraped_at.isoformat()
        
        return EventListResponse(
            events=events,
            total_count=total_count,
            last_updated=last_updated
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
            announcements=announcements,
            total_count=len(announcements)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading announcements: {str(e)}")

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


