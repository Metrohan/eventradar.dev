from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import Response
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
from ..services.rate_limiter import FixedWindowRateLimiter
from ..services.rss_service import build_events_rss
from ..services import email_service, push_service
from ..services.weekly_content_service import WeeklyContentService
from ..schemas.blog_post import BlogPostListResponse, BlogPostResponse
from ..schemas.event import EventResponse, EventListResponse
from ..schemas.announcement import AnnouncementResponse, AnnouncementListResponse
from ..schemas.suggestion import SuggestionCreate, SuggestionResponse
from ..schemas.event_request import EventRequestCreate, EventRequestResponse
from ..schemas.subscriber import (
    EmailSubscribeRequest,
    PushSubscribeRequest,
    PushUnsubscribeRequest,
)
from ..models.scraper_log import ScraperLog
from ..models.event import Event
from ..models.subscriber import Subscriber
from ..models.push_subscription import PushSubscription
import secrets

router = APIRouter()
public_form_limiter = FixedWindowRateLimiter(limit=5, window_seconds=60)


def enforce_public_form_rate_limit(request: Request) -> None:
    direct_ip = request.client.host if request.client else "unknown"
    forwarded_ip = request.headers.get("x-forwarded-for", "").split(",", 1)[0].strip()
    key = f"{direct_ip}:{forwarded_ip or direct_ip}"
    retry_after = public_form_limiter.check(key)
    if retry_after is not None:
        raise HTTPException(
            status_code=429,
            detail="Çok fazla istek gönderildi. Lütfen daha sonra tekrar deneyin.",
            headers={"Retry-After": str(max(1, int(retry_after)))},
        )


@router.get("/sources")
async def get_sources():
    """Return public metadata for enabled event-source integrations."""
    return [source.public_dict() for source in get_enabled_sources()]


@router.get("/blog", response_model=BlogPostListResponse)
async def get_blog_posts(db: Session = Depends(get_db)):
    posts = WeeklyContentService(db).list_published()
    return BlogPostListResponse(
        posts=[BlogPostResponse.model_validate(post) for post in posts],
        total_count=len(posts),
    )


@router.get("/blog/{slug}", response_model=BlogPostResponse)
async def get_blog_post(slug: str, db: Session = Depends(get_db)):
    post = WeeklyContentService(db).get_published(slug)
    if not post:
        raise HTTPException(status_code=404, detail="Blog yazısı bulunamadı")
    return post


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


@router.get("/events/rss")
async def get_events_rss(db: Session = Depends(get_db)):
    """En güncel etkinlikleri RSS 2.0 feed'i olarak döner (bkz. rss_service)."""
    event_service = EventService(db)
    events = event_service.get_events(active_only=True, limit=100)
    feed_xml = build_events_rss(events)
    return Response(content=feed_xml, media_type="application/rss+xml")


@router.post("/subscribe")
async def subscribe_email(
    payload: EmailSubscribeRequest,
    request: Request,
    db: Session = Depends(get_db),
    _rate_limit: None = Depends(enforce_public_form_rate_limit),
):
    """
    E-posta ile abone olur (hesap gerektirmez). Double opt-in: onay e-postası
    gönderilir, kullanıcı linke tıklayana kadar 'confirmed' False kalır ve
    haftalık özete dahil edilmez.
    """
    # Her durumda aynı jenerik mesaj döner (e-posta zaten kayıtlı mı diye
    # ayırt etmek, saldırganın hangi adreslerin abone olduğunu anlamasına
    # yol açar — bkz. email enumeration).
    generic_response = {
        "message": "Onay e-postası gönderildi. Lütfen gelen kutunuzu kontrol edin."
    }

    existing = (
        db.query(Subscriber)
        .filter(Subscriber.contact_info == payload.email, Subscriber.channel == "email")
        .first()
    )
    if existing:
        if not existing.confirmed:  # type: ignore[truthy-bool]
            email_service.send_confirmation_email(
                payload.email, str(existing.confirm_token)
            )
        return generic_response

    confirm_token = secrets.token_urlsafe(32)
    subscriber = Subscriber(
        contact_info=payload.email,
        channel="email",
        confirmed=False,
        confirm_token=confirm_token,
        unsubscribe_token=secrets.token_urlsafe(32),
    )
    db.add(subscriber)
    db.commit()

    email_service.send_confirmation_email(payload.email, confirm_token)
    return generic_response


@router.get("/subscribe/confirm")
async def confirm_subscription(token: str, db: Session = Depends(get_db)):
    subscriber = db.query(Subscriber).filter(Subscriber.confirm_token == token).first()
    if not subscriber:
        raise HTTPException(
            status_code=404, detail="Geçersiz veya süresi dolmuş bağlantı"
        )
    subscriber.confirmed = True  # type: ignore[assignment]
    db.commit()
    return {"message": "Aboneliğiniz onaylandı."}


@router.get("/subscribe/unsubscribe")
async def unsubscribe(token: str, db: Session = Depends(get_db)):
    subscriber = (
        db.query(Subscriber).filter(Subscriber.unsubscribe_token == token).first()
    )
    if not subscriber:
        raise HTTPException(status_code=404, detail="Geçersiz bağlantı")
    db.delete(subscriber)
    db.commit()
    return {"message": "Abonelikten çıkıldı."}


@router.post("/push/subscribe")
async def push_subscribe(
    payload: PushSubscribeRequest,
    db: Session = Depends(get_db),
    _rate_limit: None = Depends(enforce_public_form_rate_limit),
):
    if not push_service.is_valid_push_endpoint(payload.endpoint):
        raise HTTPException(status_code=400, detail="Geçersiz push endpoint")

    existing = (
        db.query(PushSubscription)
        .filter(PushSubscription.endpoint == payload.endpoint)
        .first()
    )
    if existing:
        return {"message": "Zaten abone."}

    sub = PushSubscription(
        endpoint=payload.endpoint,
        p256dh=payload.keys.get("p256dh", ""),
        auth=payload.keys.get("auth", ""),
    )
    db.add(sub)
    db.commit()
    return {"message": "Push bildirimleri etkinleştirildi."}


@router.post("/push/unsubscribe")
async def push_unsubscribe(
    payload: PushUnsubscribeRequest,
    db: Session = Depends(get_db),
    _rate_limit: None = Depends(enforce_public_form_rate_limit),
):
    db.query(PushSubscription).filter(
        PushSubscription.endpoint == payload.endpoint
    ).delete()
    db.commit()
    return {"message": "Push bildirimleri kapatıldı."}


@router.get("/push/vapid-public-key")
async def get_vapid_public_key():
    import os

    return {"key": os.getenv("VAPID_PUBLIC_KEY", "")}


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
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail="Duyuru yüklenirken bir hata oluştu"
        ) from exc


@router.get("/events/{event_id}", response_model=EventResponse)
async def get_event(event_id: int, db: Session = Depends(get_db)):
    event_service = EventService(db)
    event = event_service.get_public_event_by_id(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Etkinlik bulunamadı")
    return event


@router.get("/status")
async def get_status(db: Session = Depends(get_db)):
    """Platform sağlık durumu — scraper kayıtları, aktif etkinlik sayısı."""
    try:
        active_count = db.query(Event).filter(Event.is_active == True).count()
        total_count = db.query(Event).count()

        scrapers = []
        for source in get_enabled_sources():
            latest: Optional[ScraperLog] = (
                db.query(ScraperLog)
                .filter(ScraperLog.source.in_(source.identifiers))
                .order_by(desc(ScraperLog.created_at))
                .first()
            )
            if latest:
                scrapers.append(
                    {
                        "source": source.name,
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
    suggestion: SuggestionCreate,
    db: Session = Depends(get_db),
    _rate_limit: None = Depends(enforce_public_form_rate_limit),
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
    request: EventRequestCreate,
    db: Session = Depends(get_db),
    _rate_limit: None = Depends(enforce_public_form_rate_limit),
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
