from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="TechEventRadar API - Modern full-stack event management system",
    version="2.0.0",
    debug=settings.debug,
    default_response_class=UnicodeJSONResponse,
)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    from .core.database import SessionLocal
    from .services.tag_service import seed_tags

    db = SessionLocal()
    try:
        seed_tags(db)
    finally:
        db.close()


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
        or request.method == "OPTIONS"
    ):
        return await call_next(request)

    response = await call_next(request)

    # Log valid successful requests
    if 200 <= response.status_code < 400:
        try:
            db = SessionLocal()
            service = AnalyticsService(db)
            service.log_request(
                path=path,
                method=request.method,
                ip=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent"),
            )
            db.close()
        except Exception as e:
            print(f"Error logging traffic: {e}")

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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=settings.debug)  # nosec B104
