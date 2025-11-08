from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..core.database import get_db
from ..services.event_service import EventService
from ..services.announcement_service import AnnouncementService
from ..services.suggestion_service import SuggestionService
from ..services.event_request_service import EventRequestService
from ..services.auth_service import AuthService
from ..schemas.event import EventCreate, EventUpdate, EventResponse, EventListResponse
from ..schemas.announcement import AnnouncementCreate, AnnouncementResponse, AnnouncementListResponse
from ..schemas.suggestion import SuggestionResponse, SuggestionListResponse
from ..schemas.event_request import EventRequestResponse, EventRequestListResponse
from ..schemas.auth import LoginRequest, LoginResponse
from ..core.auth import get_current_admin

router = APIRouter()

# Authentication endpoints
@router.post("/login", response_model=LoginResponse)
async def admin_login(login_data: LoginRequest):
    """
    Admin login (converted from Flask route /admin/admin)
    """
    auth_service = AuthService()
    
    if not auth_service.authenticate_user(login_data.username, login_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    access_token = auth_service.create_access_token(data={"sub": login_data.username})
    return LoginResponse(access_token=access_token)

# Event management endpoints
@router.get("/events", response_model=EventListResponse)
async def get_admin_events(
    db: Session = Depends(get_db),
    current_admin: str = Depends(get_current_admin)
):
    """
    Get all events for admin (converted from Flask dashboard)
    """
    event_service = EventService(db)
    
    try:
        events = event_service.get_events(active_only=False)
        total_count = len(events)
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

@router.post("/events", response_model=EventResponse)
async def create_event(
    event_data: EventCreate,
    db: Session = Depends(get_db),
    current_admin: str = Depends(get_current_admin)
):
    """
    Create a new event (converted from Flask route /events/add_event)
    """
    event_service = EventService(db)
    
    try:
        event = event_service.create_event(event_data)
        return event
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating event: {str(e)}")

@router.put("/events/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: int,
    event_data: EventUpdate,
    db: Session = Depends(get_db),
    current_admin: str = Depends(get_current_admin)
):
    """
    Update an event (converted from Flask route /events/edit_event/<int:event_id>)
    """
    event_service = EventService(db)
    
    try:
        event = event_service.update_event(event_id, event_data)
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        return event
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating event: {str(e)}")

@router.delete("/events/{event_id}")
async def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_admin: str = Depends(get_current_admin)
):
    """
    Delete an event (converted from Flask route /events/delete_event/<int:event_id>)
    """
    event_service = EventService(db)
    
    try:
        success = event_service.delete_event(event_id)
        if not success:
            raise HTTPException(status_code=404, detail="Event not found")
        return {"message": "Event deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting event: {str(e)}")

# Announcement management endpoints
@router.get("/announcements", response_model=AnnouncementListResponse)
async def get_admin_announcements(
    db: Session = Depends(get_db),
    current_admin: str = Depends(get_current_admin)
):
    """
    Get all announcements for admin
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

@router.post("/announcements", response_model=AnnouncementResponse)
async def create_announcement(
    announcement_data: AnnouncementCreate,
    db: Session = Depends(get_db),
    current_admin: str = Depends(get_current_admin)
):
    """
    Create a new announcement (converted from Flask route /announcements/add_announcement)
    """
    announcement_service = AnnouncementService(db)
    
    try:
        announcement = announcement_service.create_announcement(announcement_data)
        return announcement
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating announcement: {str(e)}")

@router.delete("/announcements/{announcement_id}")
async def delete_announcement(
    announcement_id: int,
    db: Session = Depends(get_db),
    current_admin: str = Depends(get_current_admin)
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting announcement: {str(e)}")

# Suggestion management endpoints
@router.get("/suggestions", response_model=SuggestionListResponse)
async def get_suggestions(
    db: Session = Depends(get_db),
    current_admin: str = Depends(get_current_admin)
):
    """
    Get all suggestions (converted from Flask route /suggestions/suggestions)
    """
    suggestion_service = SuggestionService(db)
    
    try:
        suggestions = suggestion_service.get_suggestions()
        return SuggestionListResponse(
            suggestions=suggestions,
            total_count=len(suggestions)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading suggestions: {str(e)}")

@router.delete("/suggestions/{suggestion_id}")
async def delete_suggestion(
    suggestion_id: int,
    db: Session = Depends(get_db),
    current_admin: str = Depends(get_current_admin)
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
        raise HTTPException(status_code=500, detail=f"Error deleting suggestion: {str(e)}")

# Event request management endpoints
@router.get("/event-requests", response_model=EventRequestListResponse)
async def get_event_requests(
    db: Session = Depends(get_db),
    current_admin: str = Depends(get_current_admin)
):
    """
    Get all event requests (converted from Flask route /events/requests)
    """
    event_request_service = EventRequestService(db)
    
    try:
        requests = event_request_service.get_event_requests()
        return EventRequestListResponse(
            requests=requests,
            total_count=len(requests)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading event requests: {str(e)}")

@router.delete("/event-requests/{request_id}")
async def delete_event_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_admin: str = Depends(get_current_admin)
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
        raise HTTPException(status_code=500, detail=f"Error deleting event request: {str(e)}")

