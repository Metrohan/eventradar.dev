from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from .core.config import settings
from .core.database import engine, Base
from .api import api_router
import json


# Custom JSONResponse class with ensure_ascii=False
class UnicodeJSONResponse(JSONResponse):
    def render(self, content) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
        ).encode("utf-8")


# Create database tables


@asynccontextmanager
async def lifespan(_app: FastAPI):
    Base.metadata.create_all(bind=engine)
    from .core.database import SessionLocal
    from .services.tag_service import seed_tags

    db = SessionLocal()
    try:
        seed_tags(db)
    finally:
        db.close()
    yield


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="TechEventRadar API - Modern full-stack event management system",
    version="2.0.0",
    debug=settings.debug,
    default_response_class=UnicodeJSONResponse,
    lifespan=lifespan,
)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router)
from .api.discovery import router as discovery_router

app.include_router(discovery_router)

# Scrape-time event thumbnails (see docs/adr/0005-scrape-time-image-resize.md)
_thumbnail_dir = Path(settings.thumbnail_dir)
_thumbnail_dir.mkdir(parents=True, exist_ok=True)
app.mount(
    settings.thumbnail_public_prefix,
    StaticFiles(directory=_thumbnail_dir),
    name="thumbnails",
)

# Traffic Logging Middleware
from fastapi import Request
from .core.database import SessionLocal
from .services.analytics_service import AnalyticsService


@app.middleware("http")
async def log_traffic(request: Request, call_next):
    # Skip logging for static files, docs, and admin API
    path = request.url.path
    if (
        path.startswith("/static")
        or path.startswith("/docs")
        or path.startswith("/openapi.json")
        or path.startswith("/api/admin")
        or path.startswith("/api/seo/")  # nginx SSI subrequest, not a page view
        or request.method == "OPTIONS"
    ):
        return await call_next(request)

    response = await call_next(request)

    # Log valid successful requests
    if 200 <= response.status_code < 400:
        db = None
        try:
            db = SessionLocal()
            service = AnalyticsService(db)
            service.log_request(
                path=path,
                method=request.method,
                ip=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent"),
            )
        except Exception as e:
            print(f"Error logging traffic: {e}")
        finally:
            if db is not None:
                db.close()

    return response


@app.get("/")
async def root():
    """
    Root endpoint - API health check
    """
    return {
        "message": "TechEventRadar API is running!",
        "version": "2.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy", "message": "API is running successfully"}


ROBOTS_TXT = """\
User-agent: *
Allow: /
Disallow: /admin/
Disallow: /api/admin/
Disallow: /docs
Disallow: /openapi.json

Sitemap: https://eventradar.dev/sitemap.xml
"""


@app.get("/robots.txt", response_class=Response)
async def robots_txt():
    """
    robots.txt served from version control (see docs/adr / nginx notes).

    The production host nginx proxies GET /robots.txt here instead of serving a
    hand-edited /var/www/seo/robots.txt that the deploy pipeline never touched
    and that blanket-blocked /api/ — which also hid /api/events/rss and the
    dynamic sitemap from Google (GSC "Blocked by robots.txt").
    """
    return Response(content=ROBOTS_TXT, media_type="text/plain")


@app.get("/sitemap.xml", response_class=Response)
async def sitemap():
    from .services.sitemap_service import build_sitemap
    from .services.event_lifecycle import visible_event_filter
    from .models.event import Event
    from .models.blog_post import BlogPost

    db = SessionLocal()
    try:
        events = db.query(Event).filter(*visible_event_filter()).all()
        posts = db.query(BlogPost).filter(BlogPost.is_published.is_(True)).all()
        return Response(
            content=build_sitemap(events, posts), media_type="application/xml"
        )
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=settings.debug)  # nosec B104
