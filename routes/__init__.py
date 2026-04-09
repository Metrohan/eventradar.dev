from .public import public_bp
from .admin import admin_bp
from .events import events_bp
from .announcements import announcements_bp
from .suggestions import suggestions_bp
from .pending import pending_bp
from .requests import requests_bp

__all__ = [
    "public_bp",
    "admin_bp",
    "events_bp",
    "announcements_bp",
    "suggestions_bp",
    "pending_bp",
    "requests_bp",
]
