from datetime import date, datetime, time, timedelta

from sqlalchemy.orm import Session

from ..models.blog_post import BlogPost
from ..models.event import Event

MONTHS = (
    "Ocak",
    "Şubat",
    "Mart",
    "Nisan",
    "Mayıs",
    "Haziran",
    "Temmuz",
    "Ağustos",
    "Eylül",
    "Ekim",
    "Kasım",
    "Aralık",
)


class WeeklyContentService:
    """Create deterministic, idempotent weekly event roundups."""

    def __init__(self, db: Session, clock=datetime.now):
        self._db = db
        self._clock = clock

    def list_published(self) -> list[BlogPost]:
        return (
            self._db.query(BlogPost)
            .filter(BlogPost.is_published == True)
            .order_by(BlogPost.week_start.desc())
            .all()
        )

    def get_published(self, slug: str) -> BlogPost | None:
        return (
            self._db.query(BlogPost)
            .filter(BlogPost.slug == slug, BlogPost.is_published == True)
            .first()
        )

    def generate(self, week_start: date | None = None) -> BlogPost:
        start = week_start or self._next_monday(self._clock().date())
        existing = self._db.query(BlogPost).filter(BlogPost.week_start == start).first()
        if existing:
            return existing

        end = start + timedelta(days=6)
        events = (
            self._db.query(Event)
            .filter(
                Event.is_active == True,
                Event.date >= datetime.combine(start, time.min),
                Event.date <= datetime.combine(end, time.max),
            )
            .order_by(Event.date.asc())
            .all()
        )
        label = f"{start.day} {MONTHS[start.month - 1]} – {end.day} {MONTHS[end.month - 1]} {end.year}"
        title = f"Bu Haftanın Teknoloji Etkinlikleri: {label}"
        if events:
            lines = [
                f"## {event.title}\n\n{self._event_line(event)}\n\n{event.description or ''}\n\n[Etkinliği incele]({event.url})"
                for event in events
            ]
            content = "\n\n---\n\n".join(lines)
            summary = f"{label} haftasında gerçekleşecek {len(events)} teknoloji etkinliğini keşfet."
        else:
            content = "Bu hafta için takvimimizde henüz etkinlik bulunmuyor. Güncel fırsatlar için etkinlik listesini takip edebilirsin."
            summary = f"{label} haftasının teknoloji etkinliği özeti."

        post = BlogPost(
            slug=f"haftalik-etkinlikler-{start.isoformat()}",
            title=title,
            summary=summary,
            content=content,
            week_start=start,
            week_end=end,
            is_published=True,
            published_at=self._clock(),
        )
        self._db.add(post)
        self._db.commit()
        self._db.refresh(post)
        return post

    @staticmethod
    def _next_monday(today: date) -> date:
        return today + timedelta(days=(-today.weekday()) % 7)

    @staticmethod
    def _event_line(event: Event) -> str:
        event_date = (
            event.date.strftime("%d.%m.%Y %H:%M") if event.date else "Tarih açıklanmadı"
        )
        return f"**{event_date} · {event.location or 'Konum açıklanmadı'} · {event.source}**"
