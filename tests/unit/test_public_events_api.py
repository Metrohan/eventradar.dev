from datetime import datetime, timedelta

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api import public
from app.core.database import get_db
from app.models.event import Event
from app.schemas.event import EventResponse


@pytest.fixture
def client(test_db):
    app = FastAPI()
    app.include_router(public.router, prefix="/api")
    app.dependency_overrides[get_db] = lambda: test_db
    with TestClient(app) as client:
        yield client


@pytest.fixture
def event(test_db):
    event = Event(
        title="Hackathon",
        url="https://example.com/h",
        source="Youthall",
        date=datetime.now() + timedelta(days=5),
        image_url="https://youthall.com/uploads/source-image.png",
        thumbnail_url="/media/thumbnails/card.webp",
    )
    test_db.add(event)
    test_db.commit()
    return event


def test_public_event_list_hides_source_image_url(client, event):
    response = client.get("/api/events")

    assert response.status_code == 200
    events = response.json()["events"]
    assert events and "image_url" not in events[0]
    assert events[0]["thumbnail_url"] == "/media/thumbnails/card.webp"
    assert "source-image" not in response.text


def test_public_event_detail_hides_source_image_url(client, event):
    response = client.get(f"/api/events/{event.id}")

    assert response.status_code == 200
    assert "image_url" not in response.json()
    assert "source-image" not in response.text


def test_admin_schema_still_carries_image_url_for_the_edit_form():
    assert "image_url" in EventResponse.model_fields
