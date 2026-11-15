from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from app.core.database import get_db
from app.main import app
from app.models.ai_referral import AiReferral
from app.services.analytics_service import AnalyticsService
from app.utils.referrers import ai_source


@pytest.mark.parametrize(
    ("referer", "utm", "expected"),
    [
        ("https://chatgpt.com/", None, "chatgpt"),
        ("https://chat.openai.com/c/abc", None, "chatgpt"),
        ("https://claude.ai/chat/123", None, "claude"),
        ("https://www.perplexity.ai/search?q=x", None, "perplexity"),
        ("https://gemini.google.com/app", None, "gemini"),
        ("https://copilot.microsoft.com/", None, "copilot"),
        # the signal assistants add to the link when the browser sends no Referer
        (None, "chatgpt.com", "chatgpt"),
        (None, "ChatGPT.com ", "chatgpt"),
        (None, "perplexity", "perplexity"),
        ("https://example.org/", "claude", "claude"),
        # not an assistant
        ("https://www.google.com/", None, None),
        ("https://www.bing.com/search?q=chatgpt.com", None, None),
        ("https://gemini.google.com.evil.org/", None, None),
        ("https://notchatgpt.com/", None, None),
        ("https://example.org/", "newsletter", None),
        (None, None, None),
        ("not a url", None, None),
    ],
)
def test_ai_source_recognition(referer, utm, expected):
    assert ai_source(referer, utm) == expected


def test_service_counts_by_source_and_page_in_the_window(test_db):
    service = AnalyticsService(test_db)
    for source, path in [
        ("chatgpt", "/events/a"),
        ("chatgpt", "/events/a"),
        ("claude", "/events/b"),
    ]:
        service.log_ai_referral(source, path)
    test_db.add(
        AiReferral(
            source="perplexity",
            path="/old",
            timestamp=datetime.now() - timedelta(days=60),
        )
    )
    test_db.commit()

    stats = service.get_stats(days=30)["ai_referrals"]

    assert stats["total"] == 3  # the 60-day-old row is outside the window
    assert stats["by_source"] == [
        {"source": "chatgpt", "count": 2},
        {"source": "claude", "count": 1},
    ]
    assert stats["top_pages"][0] == {"path": "/events/a", "count": 2}


def test_purge_removes_old_referrals_with_the_traffic_log(test_db):
    test_db.add(
        AiReferral(
            source="chatgpt", path="/x", timestamp=datetime.now() - timedelta(days=200)
        )
    )
    test_db.commit()

    AnalyticsService(test_db).purge_old_logs()

    assert test_db.query(AiReferral).count() == 0


@pytest.fixture
def client(test_db, monkeypatch):
    monkeypatch.setattr("app.main.SessionLocal", lambda: test_db)
    app.dependency_overrides[get_db] = lambda: test_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.pop(get_db, None)


def _rows(db):
    return [(r.source, r.path) for r in db.query(AiReferral).all()]


def test_a_page_opened_from_an_assistant_is_counted(client, test_db):
    client.get("/sehirler", headers={"Referer": "https://chatgpt.com/"})
    client.get("/kategoriler?utm_source=claude.ai")

    assert _rows(test_db) == [("chatgpt", "/sehirler"), ("claude", "/kategoriler")]


def test_other_visits_are_not_counted(client, test_db):
    client.get("/sehirler")
    client.get("/sehirler", headers={"Referer": "https://www.google.com/"})
    # a JSON call or an image carrying an assistant Referer is not a page view
    client.get("/api/events", headers={"Referer": "https://chatgpt.com/"})
    client.post("/sehirler", headers={"Referer": "https://chatgpt.com/"})

    assert _rows(test_db) == []


def test_a_spa_page_is_counted_through_the_seo_head_subrequest(client, test_db):
    client.get("/api/seo/head/hackathonlar", headers={"Referer": "https://claude.ai/"})
    client.get("/api/seo/head/", headers={"Referer": "https://claude.ai/"})
    client.get(
        "/api/seo/head/hackathonlar", headers={"Referer": "https://example.org/"}
    )

    assert _rows(test_db) == [("claude", "/hackathonlar"), ("claude", "/")]


def test_nothing_personal_is_stored(test_db):
    columns = {c.name for c in AiReferral.__table__.columns}
    assert columns == {"id", "source", "path", "timestamp"}
