from datetime import date, datetime

from app.models.event import Event
from app.services.weekly_content_service import WeeklyContentService


def test_weekly_content_generation_is_idempotent(test_db):
    test_db.add(
        Event(
            title="AI Hackathon",
            date=datetime(2026, 7, 15, 10),
            location="Online",
            url="https://example.com/ai-hackathon",
            source="Example",
            description="Yapay zeka projeleri geliştirilen hackathon.",
            is_active=True,
        )
    )
    test_db.commit()
    service = WeeklyContentService(test_db, clock=lambda: datetime(2026, 7, 12, 9))

    first = service.generate(date(2026, 7, 13))
    second = service.generate(date(2026, 7, 13))

    assert first.id == second.id
    assert first.slug == "haftalik-etkinlikler-2026-07-13"
    assert "AI Hackathon" in first.content
    assert "1 teknoloji etkinliğini" in first.summary


def test_weekly_content_excludes_inactive_and_out_of_range_events(test_db):
    test_db.add_all(
        [
            Event(title="Inactive", date=datetime(2026, 7, 15), url="https://example.com/inactive", source="Example", is_active=False),
            Event(title="Next week", date=datetime(2026, 7, 21), url="https://example.com/next", source="Example", is_active=True),
        ]
    )
    test_db.commit()

    post = WeeklyContentService(test_db).generate(date(2026, 7, 13))

    assert "Inactive" not in post.content
    assert "Next week" not in post.content
    assert "henüz etkinlik bulunmuyor" in post.content
