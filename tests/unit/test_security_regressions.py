"""Security regressions with isolated API/database and no network delivery."""

from datetime import datetime, timedelta, timezone
import ssl
from unittest.mock import Mock, patch

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
import jwt
from starlette.requests import Request

from app.api import public, admin, admin_auth, admin_events
from app.core.auth import get_current_admin
from app.core.database import get_db
from app.services import auth_service, email_service
from app.services.rate_limiter import FixedWindowRateLimiter


@pytest.fixture
def isolated_client(test_db):
    app = FastAPI()
    app.include_router(public.router, prefix="/api")
    app.include_router(admin_auth.router, prefix="/api/admin")
    app.dependency_overrides[get_db] = lambda: test_db
    public.public_form_limiter.reset()
    limiter = getattr(admin_auth, "login_limiter", None)
    if limiter:
        limiter.reset()
    with TestClient(app) as client:
        yield client
    public.public_form_limiter.reset()
    if limiter:
        limiter.reset()


def test_forwarded_header_cannot_reset_form_budget():
    public.public_form_limiter.reset()
    try:
        for index in range(5):
            request = Request(
                {
                    "type": "http",
                    "client": ("192.0.2.1", 1000),
                    "headers": [(b"x-forwarded-for", f"198.51.100.{index}".encode())],
                }
            )
            public.enforce_public_form_rate_limit(request)
        with pytest.raises(HTTPException) as error:
            public.enforce_public_form_rate_limit(
                Request(
                    {
                        "type": "http",
                        "client": ("192.0.2.1", 1000),
                        "headers": [(b"x-forwarded-for", b"203.0.113.99")],
                    }
                )
            )
        assert error.value.status_code == 429
    finally:
        public.public_form_limiter.reset()


def test_login_attempts_are_bounded_even_with_changed_headers(isolated_client):
    results = [
        isolated_client.post(
            "/api/admin/login",
            json={"username": "wrong", "password": "wrong"},
            headers={"X-Forwarded-For": f"198.51.100.{i}"},
        )
        for i in range(11)
    ]
    assert results[0].status_code == 401
    assert results[-1].status_code == 429
    assert int(results[-1].headers["retry-after"]) > 0


def test_limiter_reclaims_expired_clients():
    now = [0.0]
    limiter = FixedWindowRateLimiter(1, 10, clock=lambda: now[0])
    for i in range(100):
        limiter.check(str(i))
    now[0] = 11
    limiter.check("new")
    assert len(limiter._requests) == 1


def test_limiter_capacity_does_not_evict_active_budgets():
    limiter = FixedWindowRateLimiter(1, 10, max_keys=2, clock=lambda: 0)
    assert limiter.check("first") is None
    assert limiter.check("second") is None
    assert limiter.check("third") == 10
    assert limiter.check("first") == 10


def test_token_lifetime_is_independent_of_local_timezone(monkeypatch):
    class LocalClock(datetime):
        @classmethod
        def now(cls, tz=None):
            instant = datetime(2030, 1, 1, tzinfo=timezone.utc)
            return (
                instant.astimezone(tz)
                if tz
                else instant.replace(tzinfo=None) + timedelta(hours=3)
            )

    monkeypatch.setattr(auth_service, "datetime", LocalClock)
    token = auth_service.AuthService().create_access_token({"sub": "testadmin"})
    assert jwt.decode(token, options={"verify_signature": False})["exp"] == 1893457800


@pytest.mark.parametrize(
    "payload",
    [
        {"sub": "testadmin"},
        {"sub": "old-admin", "exp": 4102444800},
        {"sub": "testadmin", "exp": 1},
    ],
)
def test_invalid_admin_claims_rejected(payload):
    token = jwt.encode(
        payload, auth_service.SECRET_KEY, algorithm=auth_service.ALGORITHM
    )
    assert auth_service.AuthService().verify_token(token) is None


def test_auth_does_not_log_token_material(caplog):
    token = auth_service.AuthService().create_access_token({"sub": "testadmin"})
    assert get_current_admin(Mock(credentials=token)) == "testadmin"
    assert token[-10:] not in caplog.text


SUGGESTION = {
    "suggestion_type": "oneri",
    "suggestion_title": "Title",
    "suggestion_text": "A long enough suggestion text.",
}
EVENT_REQUEST = {"event_link": "https://example.com/e", "event_title": "Some event"}


@pytest.mark.parametrize(
    "http_method,path,body,target,attr",
    [
        ("get", "/api/events", None, public.EventService, "get_events"),
        (
            "get",
            "/api/announcements",
            None,
            public.AnnouncementService,
            "get_announcements",
        ),
        ("get", "/api/status", None, public, "get_enabled_sources"),
        (
            "post",
            "/api/suggestions",
            SUGGESTION,
            public.SuggestionService,
            "create_suggestion",
        ),
        (
            "post",
            "/api/event-requests",
            EVENT_REQUEST,
            public.EventRequestService,
            "create_event_request",
        ),
    ],
)
def test_public_errors_hide_database_details(
    isolated_client, monkeypatch, http_method, path, body, target, attr
):
    monkeypatch.setattr(
        target, attr, Mock(side_effect=RuntimeError("SECRET_SQL_PARAMETER"))
    )
    response = getattr(isolated_client, http_method)(
        path, **({"json": body} if body else {})
    )
    assert response.status_code == 500
    assert "SECRET_SQL_PARAMETER" not in response.text


def test_status_does_not_expose_scraper_error_text(isolated_client, test_db):
    from app.models.scraper_log import ScraperLog

    name = public.get_enabled_sources()[0].name
    test_db.add(
        ScraperLog(source=name, status="failed", error_message="SECRET_STACK_TRACE")
    )
    test_db.commit()
    response = isolated_client.get("/api/status")
    assert response.status_code == 200
    assert "SECRET_STACK_TRACE" not in response.text
    assert response.json()["scrapers"][0]["error"] == "Source temporarily unavailable"


def _client_ip_seen_by_uvicorn(trusted, peer, forwarded):
    import asyncio
    from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

    seen = {}

    async def app(scope, receive, send):
        seen["client"] = scope["client"][0]

    scope = {
        "type": "http",
        "client": (peer, 5000),
        "headers": [(b"x-forwarded-for", forwarded.encode())],
    }
    asyncio.run(ProxyHeadersMiddleware(app, trusted_hosts=trusted)(scope, None, None))
    return seen["client"]


def test_forwarded_ip_honored_only_from_trusted_proxy():
    trusted = "172.16.0.0/12"
    # nginx container (trusted) appends the docker gateway to the client's address
    assert (
        _client_ip_seen_by_uvicorn(trusted, "172.18.0.3", "203.0.113.9, 172.18.0.1")
        == "203.0.113.9"
    )
    # an untrusted peer cannot choose its own identity
    assert (
        _client_ip_seen_by_uvicorn(trusted, "198.51.100.7", "203.0.113.9")
        == "198.51.100.7"
    )


def test_compose_backend_trusts_proxy_headers_from_configured_range():
    from pathlib import Path

    compose = (Path(__file__).parents[2] / "docker-compose.yml").read_text()
    command = next(l for l in compose.splitlines() if "uvicorn app.main:app" in l)
    assert "--proxy-headers" in command
    assert "--forwarded-allow-ips" in command and "FORWARDED_ALLOW_IPS" in command
    assert (
        "forwarded-allow-ips *" not in command
        and "forwarded-allow-ips=*" not in command
    )


def test_smtp_verifies_certificate_and_hostname(monkeypatch):
    monkeypatch.setattr(email_service.settings, "smtp_host", "smtp.example.com")
    monkeypatch.setattr(email_service.settings, "smtp_user", "test-user")
    monkeypatch.setattr(email_service.settings, "smtp_pass", "test-password")
    with patch.object(email_service.smtplib, "SMTP") as smtp:
        assert email_service._send("reader@example.com", "test", "<p>hello</p>")
    context = smtp.return_value.__enter__.return_value.starttls.call_args.kwargs.get(
        "context"
    )
    assert context is not None
    assert context.verify_mode == ssl.CERT_REQUIRED
    assert context.check_hostname


def test_digest_treats_scraped_fields_as_text():
    with patch.object(email_service, "_send", return_value=True) as send:
        email_service.send_weekly_digest_email(
            "reader@example.com",
            [
                {
                    "id": 1,
                    "title": '<a href="https://evil.example">claim</a>',
                    "source": "<img src=x>",
                }
            ],
            "test-token",
        )
    html = send.call_args.args[2]
    assert '<a href="https://evil.example">' not in html
    assert "<img src=x>" not in html
    assert "&lt;img src=x&gt;" in html


@pytest.mark.parametrize(
    "http_method,path,target,attr",
    [
        ("get", "/api/admin/events", admin_events.EventService, "get_events"),
        (
            "get",
            "/api/admin/announcements",
            admin.AnnouncementService,
            "get_announcements",
        ),
        (
            "delete",
            "/api/admin/announcements/1",
            admin.AnnouncementService,
            "delete_announcement",
        ),
        ("get", "/api/admin/suggestions", admin.SuggestionService, "get_suggestions"),
        (
            "delete",
            "/api/admin/suggestions/1",
            admin.SuggestionService,
            "delete_suggestion",
        ),
        (
            "get",
            "/api/admin/event-requests",
            admin.EventRequestService,
            "get_event_requests",
        ),
        (
            "delete",
            "/api/admin/event-requests/1",
            admin.EventRequestService,
            "delete_event_request",
        ),
        (
            "post",
            "/api/admin/announcements",
            admin.AnnouncementService,
            "create_announcement",
        ),
        ("post", "/api/admin/events", admin_events.EventService, "create_event"),
        ("put", "/api/admin/events/1", admin_events.EventService, "update_event"),
        ("delete", "/api/admin/events/1", admin_events.EventService, "delete_event"),
    ],
)
def test_admin_errors_hide_database_details(
    test_db, monkeypatch, http_method, path, target, attr
):
    app = FastAPI()
    app.include_router(admin.router, prefix="/api/admin")
    app.dependency_overrides[get_db] = lambda: test_db
    app.dependency_overrides[get_current_admin] = lambda: "testadmin"
    monkeypatch.setattr(
        target, attr, Mock(side_effect=RuntimeError("SECRET_SQL_PARAMETER"))
    )
    bodies = {
        "/api/admin/announcements": {"title": "t", "message": "m"},
        "/api/admin/events": {"title": "t", "url": "https://example.com/e"},
        "/api/admin/events/1": {"title": "t"},
    }
    with TestClient(app) as client:
        kwargs = {"json": bodies[path]} if http_method in ("post", "put") else {}
        response = getattr(client, http_method)(path, **kwargs)
    assert response.status_code == 500
    assert "SECRET_SQL_PARAMETER" not in response.text


@pytest.mark.parametrize(
    "path,service,method",
    [
        (
            "/api/admin/announcements/999",
            admin.AnnouncementService,
            "delete_announcement",
        ),
        ("/api/admin/suggestions/999", admin.SuggestionService, "delete_suggestion"),
        (
            "/api/admin/event-requests/999",
            admin.EventRequestService,
            "delete_event_request",
        ),
    ],
)
def test_admin_delete_of_missing_record_is_404(
    test_db, monkeypatch, path, service, method
):
    app = FastAPI()
    app.include_router(admin.router, prefix="/api/admin")
    app.dependency_overrides[get_db] = lambda: test_db
    app.dependency_overrides[get_current_admin] = lambda: "testadmin"
    monkeypatch.setattr(service, method, Mock(return_value=False))
    with TestClient(app) as client:
        assert client.delete(path).status_code == 404


def _post_suggestion(client, **overrides):
    body = {**SUGGESTION, **overrides}
    return client.post("/api/suggestions", json=body)


def test_suggestion_is_mailed_to_owner_with_safe_header_and_escaped_body(
    isolated_client, monkeypatch
):
    monkeypatch.setattr(
        email_service.settings, "feedback_notify_email", "owner@example.com"
    )
    sent = Mock(return_value=True)
    monkeypatch.setattr(email_service, "_send", sent)
    response = _post_suggestion(
        isolated_client,
        suggestion_title="Hello\r\nBcc: evil@example.com",
        suggestion_text="<script>alert(1)</script> and a long enough text",
    )
    assert response.status_code == 200
    (to, subject, html), kwargs = sent.call_args
    assert to == "owner@example.com"
    assert "\n" not in subject and "\r" not in subject
    assert "<script>" not in html and "&lt;script&gt;" in html
    assert "<script>" in kwargs["text_body"]  # plain text part is not HTML


def test_suggestion_without_notify_address_sends_nothing(isolated_client, monkeypatch):
    monkeypatch.setattr(email_service.settings, "feedback_notify_email", "")
    sent = Mock()
    monkeypatch.setattr(email_service, "_send", sent)
    assert _post_suggestion(isolated_client).status_code == 200
    sent.assert_not_called()


def test_suggestion_still_saved_when_mail_fails(isolated_client, test_db, monkeypatch):
    from app.models.suggestion import Suggestion

    monkeypatch.setattr(
        email_service.settings, "feedback_notify_email", "owner@example.com"
    )
    monkeypatch.setattr(
        email_service, "_send", Mock(side_effect=RuntimeError("smtp down"))
    )
    assert _post_suggestion(isolated_client).status_code == 200
    assert test_db.query(Suggestion).count() == 1


def test_event_request_is_mailed_to_owner_with_safe_header_and_escaped_body(
    isolated_client, monkeypatch
):
    monkeypatch.setattr(
        email_service.settings, "feedback_notify_email", "owner@example.com"
    )
    sent = Mock(return_value=True)
    monkeypatch.setattr(email_service, "_send", sent)
    response = isolated_client.post(
        "/api/event-requests",
        json={
            **EVENT_REQUEST,
            "event_title": "Meetup\r\nBcc: evil@example.com",
            "event_description": "<img src=x onerror=alert(1)>",
            "contact_email": "visitor@example.com",
        },
    )
    assert response.status_code == 200
    (to, subject, html), kwargs = sent.call_args
    assert to == "owner@example.com"
    assert "\n" not in subject and "\r" not in subject
    assert "<img" not in html and "&lt;img" in html
    assert "visitor@example.com" in kwargs["text_body"]
    assert kwargs["reply_to"] == "visitor@example.com"
    assert "https://example.com/e" in kwargs["text_body"]


def test_event_request_still_saved_when_mail_fails(
    isolated_client, test_db, monkeypatch
):
    from app.models.event_request import EventRequest

    monkeypatch.setattr(
        email_service.settings, "feedback_notify_email", "owner@example.com"
    )
    monkeypatch.setattr(
        email_service, "_send", Mock(side_effect=RuntimeError("smtp down"))
    )
    assert (
        isolated_client.post("/api/event-requests", json=EVENT_REQUEST).status_code
        == 200
    )
    assert test_db.query(EventRequest).count() == 1


def test_event_request_without_contact_email_has_no_reply_to(
    isolated_client, monkeypatch
):
    monkeypatch.setattr(
        email_service.settings, "feedback_notify_email", "owner@example.com"
    )
    sent = Mock(return_value=True)
    monkeypatch.setattr(email_service, "_send", sent)
    assert (
        isolated_client.post("/api/event-requests", json=EVENT_REQUEST).status_code
        == 200
    )
    assert sent.call_args.kwargs["reply_to"] is None


@pytest.mark.parametrize(
    "bad",
    ["a@b.com\r\nBcc: evil@example.com", "not an address", "two@a.com three@b.com"],
)
def test_unsafe_reply_to_is_dropped(monkeypatch, bad):
    monkeypatch.setattr(
        email_service.settings, "feedback_notify_email", "owner@example.com"
    )
    sent = Mock(return_value=True)
    monkeypatch.setattr(email_service, "_send", sent)
    email_service.send_event_request_notification("https://e.com", "t", None, None, bad)
    assert sent.call_args.kwargs["reply_to"] is None


@pytest.mark.parametrize(
    "host,expected",
    [
        ("203.0.113.9", "203.0.113.9"),
        ("::ffff:203.0.113.9", "203.0.113.9"),
        ("2001:db8:abcd:12:1:2:3:4", "2001:db8:abcd:12::/64"),
        ("2001:db8:abcd:12:ffff:ffff:ffff:ffff", "2001:db8:abcd:12::/64"),
        ("unknown", "unknown"),
    ],
)
def test_client_key_groups_ipv6_by_64(host, expected):
    from app.services.rate_limiter import client_key

    assert client_key(host) == expected


def test_ipv6_client_cannot_mint_keys_to_bypass_or_fill_the_limiter():
    from app.services.rate_limiter import client_key

    limiter = FixedWindowRateLimiter(limit=2, window_seconds=60, max_keys=4)
    hosts = [f"2001:db8:abcd:12::{i:x}" for i in range(1, 9)]  # one /64
    results = [limiter.check(client_key(h)) for h in hosts]
    assert results[:2] == [None, None] and all(r is not None for r in results[2:])
    assert limiter.check(client_key("198.51.100.1")) is None  # table not filled
