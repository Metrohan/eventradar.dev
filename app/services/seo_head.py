"""Per-URL <head> tags for the SPA shell (docs/adr/0008-ssi-seo-head.md).

nginx includes the fragment built here into index.html (SSI), so crawlers that
do not run JavaScript still get the right title, canonical, Open Graph tags and
Event JSON-LD, and unknown URLs get `noindex`. The values mirror what the React
pages set after load (setPageSEO / EventDetailPage); keep the two in sync.
"""

from __future__ import annotations

import html
import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from urllib.parse import urlparse

from sqlalchemy.orm import Session

from ..models.blog_post import BlogPost
from ..models.event import Event
from .event_service import EventService
from .image_pipeline import MONTHS_TR

SITE_URL = "https://eventradar.dev"
BANNER_URL = f"{SITE_URL}/banner.png"
DEFAULT_TITLE = "TechEventRadar | Bootcamp, Hackathon & Kariyer Etkinlikleri"
DEFAULT_DESCRIPTION = (
    "Türkiye'deki bootcamp, hackathon ve kariyer etkinliklerini tek yerden "
    "ücretsiz takip et. 10 kaynaktan günlük güncellenen etkinlik platformu."
)

# path -> (title, description); mirrors frontend/src/pages/** SEO calls.
STATIC_PAGES: dict[str, tuple[str, str]] = {
    "/": (DEFAULT_TITLE, DEFAULT_DESCRIPTION),
    "/takvim": (
        "Etkinlik Takvimi | TechEventRadar",
        "Türkiye'deki teknoloji etkinliklerini aylık takvim görünümünde keşfet.",
    ),
    "/hackathonlar": (
        "Hackathon Etkinlikleri | TechEventRadar",
        "Türkiye'deki güncel hackathon etkinliklerini tek listede keşfet. "
        "TechCareer, Kodluyoruz, Youthall ve daha fazla kaynaktan otomatik "
        "güncellenen hackathon takvimi.",
    ),
    "/bootcamplar": (
        "Bootcamp Etkinlikleri | TechEventRadar",
        "Türkiye'deki ücretsiz ve ücretli bootcamp programlarını tek listede "
        "keşfet. Yazılım, veri bilimi ve daha fazlası için güncel bootcamp takvimi.",
    ),
    "/online-etkinlikler": (
        "Online Teknoloji Etkinlikleri | TechEventRadar",
        "Evden katılabileceğin online hackathon, webinar ve bootcamp "
        "etkinliklerini tek listede keşfet.",
    ),
    "/bu-haftaki-etkinlikler": (
        "Bu Hafta Başvurabileceğin Etkinlikler | TechEventRadar",
        "Önümüzdeki 7 gün içinde gerçekleşecek hackathon, bootcamp ve webinar "
        "etkinliklerini tek listede keşfet.",
    ),
    "/son-basvurular": (
        "Son Başvuru Tarihi Yaklaşan Etkinlikler | TechEventRadar",
        "Başvuru son tarihi bu hafta dolacak hackathon, bootcamp ve webinar "
        "etkinliklerini kaçırma.",
    ),
    "/bootcamp-rehberi": (
        "Türkiye Ücretsiz Bootcamp Rehberi 2026 | TechEventRadar",
        "Türkiye'deki ücretsiz bootcamp, hackathon ve kariyer etkinliklerinin "
        "tam listesi. 2026 güncel.",
    ),
    "/egitim-kaynaklari": (
        "Ücretsiz Eğitim Kaynakları | TechEventRadar",
        "Google, AWS, Microsoft ve diğer teknoloji şirketlerinin sunduğu "
        "ücretsiz eğitim, sertifika ve öğrenme kaynaklarını tek listede keşfet.",
    ),
    "/blog": (
        "Haftalık Teknoloji Etkinlikleri | TechEventRadar",
        "Her hafta öne çıkan hackathon, bootcamp, seminer ve teknoloji "
        "etkinliklerini keşfet.",
    ),
    "/etkinlik-talep": (
        "Etkinlik Ekleme Talebi | TechEventRadar",
        "Kaçırdığımız bir hackathon, bootcamp veya kariyer etkinliği mi var? "
        "TechEventRadar'a ekleyelim.",
    ),
    "/oneri-sikayet": (
        "Öneri ve Şikayet Bildir | TechEventRadar",
        "TechEventRadar hakkında öneri, hata bildirimi veya şikayetinizi bize iletin.",
    ),
}

_EVENT_RE = re.compile(r"^/etkinlik/(\d{1,9})$")
_BLOG_RE = re.compile(r"^/blog/([A-Za-z0-9_-]{1,255})$")
_ONLINE_RE = re.compile(r"online|çevrim\s?içi", re.IGNORECASE)


@dataclass
class _Meta:
    title: str
    description: str
    path: str | None  # canonical path; None means noindex and no canonical
    image: str = BANNER_URL
    json_ld: list[tuple[str, dict]] = field(default_factory=list)  # (script id, data)


def _esc(value: str) -> str:
    return html.escape(value, quote=True)


def _ld_json(data: dict) -> str:
    """Same escaping as the client's JSON-LD injection (no </script> breakout)."""
    return (
        json.dumps(data, ensure_ascii=False)
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("&", "\\u0026")
        .replace(" ", "\\u2028")
        .replace(" ", "\\u2029")
    )


def _render(meta: _Meta) -> str:
    title, desc = _esc(meta.title), _esc(meta.description)
    robots = "index, follow" if meta.path is not None else "noindex, follow"
    lines = [
        f"<title>{title}</title>",
        f'<meta name="description" content="{desc}" />',
        f'<meta name="robots" content="{robots}" />',
    ]
    if meta.path is not None:
        url = _esc(SITE_URL + ("" if meta.path == "/" else meta.path))
        lines.append(f'<link rel="canonical" href="{url}" />')
        lines.append(f'<meta property="og:url" content="{url}" />')
    lines += [
        f'<meta property="og:title" content="{title}" />',
        f'<meta property="og:description" content="{desc}" />',
        '<meta property="og:type" content="website" />',
        f'<meta property="og:image" content="{_esc(meta.image)}" />',
    ]
    if meta.image == BANNER_URL:
        lines += [
            '<meta property="og:image:width" content="1200" />',
            '<meta property="og:image:height" content="630" />',
        ]
    lines += [
        '<meta name="twitter:card" content="summary_large_image" />',
        f'<meta name="twitter:title" content="{title}" />',
        f'<meta name="twitter:description" content="{desc}" />',
        f'<meta name="twitter:image" content="{_esc(meta.image)}" />',
    ]
    for script_id, data in meta.json_ld:
        lines.append(
            f'<script id="{script_id}" type="application/ld+json">'
            f"{_ld_json(data)}</script>"
        )
    return "\n".join(lines) + "\n"


def _http_origin(url: str | None) -> str | None:
    parsed = urlparse(url or "")
    if parsed.scheme in ("http", "https") and parsed.netloc:
        return f"{parsed.scheme}://{parsed.netloc}"
    return None


def _event_meta(event: Event) -> _Meta:
    date: datetime | None = event.date  # type: ignore[assignment]
    title = str(event.title)
    path = f"/etkinlik/{event.id}"
    parts = [title]
    if date:
        parts.append(f"{date.day:02d} {MONTHS_TR[date.month - 1]} {date.year}")
    if event.location:
        parts.append(str(event.location))
    description = " — ".join(parts) + ". Teknoloji ve kariyer etkinliği."

    card = str(event.thumbnail_url or "")
    image = SITE_URL + card if card.startswith("/") else BANNER_URL

    json_ld: list[tuple[str, dict]] = []
    if date:  # Google's Event rich result requires startDate
        location_text = str(event.location or "")
        is_online = bool(_ONLINE_RE.search(location_text))
        source_url = str(event.url or "")
        origin = _http_origin(source_url)
        organization = {
            "@type": "Organization",
            "name": str(event.source),
            **({"url": origin} if origin else {}),
        }
        schema: dict = {
            "@context": "https://schema.org",
            "@type": "Event",
            "name": title,
            # Naive ISO on purpose: Google reads a date without offset as local
            # to the event, which is what the scrapers store.
            "startDate": date.isoformat(),
            "url": SITE_URL + path,
            "eventStatus": "https://schema.org/EventScheduled",
            "eventAttendanceMode": (
                "https://schema.org/OnlineEventAttendanceMode"
                if is_online
                else "https://schema.org/OfflineEventAttendanceMode"
            ),
            "location": (
                {"@type": "VirtualLocation", "url": source_url}
                if is_online
                else {
                    "@type": "Place",
                    "name": location_text,
                    "address": location_text,
                }
            ),
            "organizer": organization,
            "performer": organization,
        }
        if event.description:
            schema["description"] = str(event.description)
        if image != BANNER_URL:
            schema["image"] = image
        if not location_text:
            schema.pop("location", None)
            schema.pop("eventAttendanceMode", None)
        json_ld.append(("event-jsonld", schema))

    json_ld.append(
        (
            "breadcrumb-jsonld",
            {
                "@context": "https://schema.org",
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {
                        "@type": "ListItem",
                        "position": 1,
                        "name": "Ana Sayfa",
                        "item": SITE_URL,
                    },
                    {
                        "@type": "ListItem",
                        "position": 2,
                        "name": title,
                        "item": SITE_URL + path,
                    },
                ],
            },
        )
    )
    return _Meta(f"{title} | TechEventRadar", description, path, image, json_ld)


def _normalize(path: str) -> str:
    return "/" + path.strip("/")


def build_head(path: str, db: Session) -> str:
    """HTML fragment of <head> tags for `path`; unknown or missing -> noindex."""
    path = _normalize(path)
    meta: _Meta | None = None

    if path in STATIC_PAGES:
        title, description = STATIC_PAGES[path]
        meta = _Meta(title, description, path)
    elif match := _EVENT_RE.match(path):
        event = EventService(db).get_public_event_by_id(int(match.group(1)))
        meta = _event_meta(event) if event else None
    elif match := _BLOG_RE.match(path):
        post = (
            db.query(BlogPost)
            .filter(BlogPost.slug == match.group(1), BlogPost.is_published.is_(True))
            .first()
        )
        if post:
            meta = _Meta(f"{post.title} | TechEventRadar", str(post.summary), path)

    return _render(meta or _Meta(DEFAULT_TITLE, DEFAULT_DESCRIPTION, None))
