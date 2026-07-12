from xml.sax.saxutils import escape
from email.utils import format_datetime
from datetime import datetime, timezone

from ..models.event import Event

SITE_URL = "https://eventradar.dev"
FEED_ITEM_LIMIT = 50


def _rfc822(dt: datetime | None) -> str:
    if dt is None:
        dt = datetime.now(timezone.utc)
    elif dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return format_datetime(dt)


def build_events_rss(events: list[Event]) -> str:
    """
    En güncel etkinlikleri RFC 2.0 uyumlu bir RSS feed'e dönüştürür.

    Etkinlik sayısı FEED_ITEM_LIMIT ile sınırlanır; öğeler `scraped_at`'e
    göre en yeniden eskiye sıralanır (yeni eklenen etkinlikleri takip etmek
    isteyen abonelere en anlamlı sıralama budur).
    """
    items = sorted(events, key=lambda e: e.scraped_at or datetime.min, reverse=True)[
        :FEED_ITEM_LIMIT
    ]

    item_xml = []
    for event in items:
        link = f"{SITE_URL}/etkinlik/{event.id}"
        title = str(event.title or "")
        description = escape(str(event.description or "").strip()[:500])
        item_xml.append(
            "<item>"
            f"<title>{escape(title)}</title>"
            f"<link>{escape(link)}</link>"
            f'<guid isPermaLink="true">{escape(link)}</guid>'
            f"<description>{description}</description>"
            f"<pubDate>{_rfc822(event.scraped_at)}</pubDate>"  # type: ignore[arg-type]
            "</item>"
        )

    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<rss version="2.0">'
        "<channel>"
        "<title>TechEventRadar - Etkinlikler</title>"
        f"<link>{SITE_URL}</link>"
        "<description>Türkiye'deki güncel teknoloji etkinlikleri (hackathon, "
        "bootcamp, seminer, webinar)</description>"
        "<language>tr-TR</language>"
        f"<lastBuildDate>{_rfc822(datetime.now(timezone.utc))}</lastBuildDate>"
        + "".join(item_xml)
        + "</channel>"
        "</rss>"
    )
