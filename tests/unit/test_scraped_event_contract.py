import pytest

from app.services.event_ingestion import ScrapedEvent


@pytest.mark.parametrize(
    "payload",
    [
        {"title": "Event", "url": "https://example.com/event"},
        {
            "title": "Event",
            "url": "https://example.com/event",
            "description": "Description",
            "date": "2027-01-01T10:00:00",
            "application_deadline": "2026-12-30T10:00:00",
            "location": "Online",
            "image_url": "https://example.com/image.png",
        },
    ],
)
def test_scraper_mapping_adapter_produces_canonical_event(payload):
    event = ScrapedEvent.from_mapping(payload, "Test Source")

    assert event.title == payload["title"]
    assert event.url == payload["url"]
    assert event.source == "Test Source"
