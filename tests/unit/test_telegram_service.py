# tests/unit/test_telegram_service.py
import os
os.environ.setdefault("ALLOW_INSECURE_DEFAULTS", "true")
os.environ.setdefault("SECRET_KEY", "test-secret-key-that-is-at-least-32-chars")
os.environ.setdefault("ADMIN_USERNAME", "testadmin")
os.environ.setdefault("ADMIN_PASSWORD", "testpassword")

import pytest
from unittest.mock import patch, MagicMock


def test_not_configured_when_env_missing(monkeypatch):
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.delenv("TELEGRAM_CHANNEL_ID", raising=False)
    import importlib
    import app.services.telegram_service as ts
    importlib.reload(ts)
    assert ts._is_configured() is False


def test_configured_when_both_env_set(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123:ABC")
    monkeypatch.setenv("TELEGRAM_CHANNEL_ID", "@testchannel")
    import importlib
    import app.services.telegram_service as ts
    importlib.reload(ts)
    assert ts._is_configured() is True


def test_format_event_message_contains_title():
    import importlib
    import app.services.telegram_service as ts
    importlib.reload(ts)
    event = {
        "title": "KKB Hackathon",
        "url": "https://coderspace.io/etkinlikler/kkb/",
        "source": "Coderspace",
        "date": "16 November 2026",
        "description": "Yapay zeka hackathonu.",
        "image_url": "",
    }
    msg = ts._format_event_message(event)
    assert "KKB Hackathon" in msg
    assert "Coderspace" in msg
    assert "https://coderspace.io/etkinlikler/kkb/" in msg


def test_format_event_message_truncates_long_description():
    import importlib
    import app.services.telegram_service as ts
    importlib.reload(ts)
    event = {
        "title": "Test Event",
        "url": "https://example.com",
        "source": "Test",
        "date": "",
        "description": "A" * 300,
        "image_url": "",
    }
    msg = ts._format_event_message(event)
    assert "..." in msg
    lines = msg.split("\n")
    desc_line = [l for l in lines if l.startswith("📝")]
    assert len(desc_line[0]) <= 210


def test_detect_type():
    import importlib
    import app.services.telegram_service as ts
    importlib.reload(ts)
    assert ts._detect_type("KKB Hackathon 2026") == "hackathon"
    assert ts._detect_type("Python Bootcamp Istanbul") == "bootcamp"
    assert ts._detect_type("Vodafone Staj Programı") == "staj"
    assert ts._detect_type("AI Webinar Serisi") == "seminer"
    assert ts._detect_type("Teknoloji Zirvesi") == "diğer"
