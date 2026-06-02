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


def test_send_message_calls_requests_post(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123:ABC")
    monkeypatch.setenv("TELEGRAM_CHANNEL_ID", "@ch")
    import importlib
    import app.services.telegram_service as ts

    importlib.reload(ts)

    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None

    with patch(
        "app.services.telegram_service.requests.post", return_value=mock_resp
    ) as mock_post:
        result = ts._send_message("test mesajı")

    assert result is True
    mock_post.assert_called_once()
    call_kwargs = mock_post.call_args
    assert "test mesajı" in str(call_kwargs)
    assert "HTML" in str(call_kwargs)


def test_send_message_returns_false_when_not_configured(monkeypatch):
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.delenv("TELEGRAM_CHANNEL_ID", raising=False)
    import importlib
    import app.services.telegram_service as ts

    importlib.reload(ts)
    result = ts._send_message("test")
    assert result is False


def test_notify_new_events_noop_when_empty(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123:ABC")
    monkeypatch.setenv("TELEGRAM_CHANNEL_ID", "@ch")
    import importlib
    import app.services.telegram_service as ts

    importlib.reload(ts)

    with patch("app.services.telegram_service._send_message") as mock_send:
        ts.notify_new_events([])
    mock_send.assert_not_called()


def test_notify_new_events_sends_per_event(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123:ABC")
    monkeypatch.setenv("TELEGRAM_CHANNEL_ID", "@ch")
    import importlib
    import app.services.telegram_service as ts

    importlib.reload(ts)

    events = [
        {
            "title": "A",
            "url": "https://a.com",
            "source": "S",
            "date": "",
            "description": "",
            "image_url": "",
        },
        {
            "title": "B",
            "url": "https://b.com",
            "source": "S",
            "date": "",
            "description": "",
            "image_url": "",
        },
    ]
    with patch("app.services.telegram_service._send_message") as mock_send, patch(
        "app.services.telegram_service.time.sleep"
    ) as mock_sleep:
        ts.notify_new_events(events)

    assert mock_send.call_count == 2
    mock_sleep.assert_called_once_with(0.5)


def test_send_daily_digest_noop_when_empty(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123:ABC")
    monkeypatch.setenv("TELEGRAM_CHANNEL_ID", "@ch")
    import importlib
    import app.services.telegram_service as ts

    importlib.reload(ts)

    with patch("app.services.telegram_service._send_message") as mock_send:
        ts.send_daily_digest([], "1 Haziran 2026")
    mock_send.assert_not_called()


def test_send_weekly_digest_sends_even_when_empty(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123:ABC")
    monkeypatch.setenv("TELEGRAM_CHANNEL_ID", "@ch")
    import importlib
    import app.services.telegram_service as ts

    importlib.reload(ts)

    with patch("app.services.telegram_service._send_message") as mock_send:
        ts.send_weekly_digest([], "26 Mayıs – 1 Haziran")

    mock_send.assert_called_once()
    assert "yeni etkinlik eklenmedi" in mock_send.call_args[0][0]
