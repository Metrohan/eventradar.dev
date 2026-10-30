from ..utils.event_urls import event_path
from xml.sax.saxutils import escape
from datetime import datetime, timezone

from ..models.event import Event
from ..models.blog_post import BlogPost
from .location_normalizer import CITY_NAMES

SITE_URL = "https://eventradar.dev"

STATIC_PAGES = [
    ("", "daily", "1.0"),
    ("/kategoriler", "daily", "0.7"),
    ("/sehirler", "daily", "0.7"),
    ("/blog", "weekly", "0.6"),
    ("/takvim", "daily", "0.8"),
    ("/hackathonlar", "daily", "0.9"),
    ("/bootcamplar", "daily", "0.9"),
    ("/online-etkinlikler", "daily", "0.9"),
    ("/bu-haftaki-etkinlikler", "daily", "0.8"),
    ("/son-basvurular", "daily", "0.8"),
    ("/bootcamp-rehberi", "weekly", "0.7"),
    ("/egitim-kaynaklari", "weekly", "0.6"),
    ("/etkinlik-talep", "monthly", "0.4"),
]


def _w3c_date(dt: datetime | None) -> str:
    if dt is None:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.strftime("%Y-%m-%d")


def build_sitemap(events: list[Event], posts: list[BlogPost]) -> str:
    urls: list[str] = []

    for path, changefreq, priority in STATIC_PAGES:
        urls.append(
            f"  <url>\n"
            f"    <loc>{escape(SITE_URL + path)}</loc>\n"
            f"    <changefreq>{changefreq}</changefreq>\n"
            f"    <priority>{priority}</priority>\n"
            f"  </url>"
        )

    for event in events:
        loc = escape(f"{SITE_URL}{event_path(event)}")
        lastmod = _w3c_date(
            getattr(event, "last_seen_at", None) or getattr(event, "scraped_at", None)
        )
        urls.append(
            f"  <url>\n"
            f"    <loc>{loc}</loc>\n"
            f"    <lastmod>{lastmod}</lastmod>\n"
            f"    <changefreq>weekly</changefreq>\n"
            f"    <priority>0.7</priority>\n"
            f"  </url>"
        )

    categories: set[str] = set()
    cities: set[str] = set()
    for event in events:
        tags = getattr(event, "tags", [])
        if isinstance(tags, (list, tuple)):
            categories.update(str(tag.name) for tag in tags)
        for slug, city in CITY_NAMES.items():
            if getattr(event, "location", None) == city:
                cities.add(slug)
    import re

    paths = [
        "/kategoriler/" + name
        for name in sorted(categories)
        if re.fullmatch(r"[a-z0-9-]+", name)
    ]
    paths += ["/sehirler/" + name for name in sorted(cities)]
    for path in paths:
        urls.append(f"  <url><loc>{escape(SITE_URL + path)}</loc></url>")

    for post in posts:
        loc = escape(f"{SITE_URL}/blog/{post.slug}")
        lastmod = _w3c_date(getattr(post, "created_at", None))
        urls.append(
            f"  <url>\n"
            f"    <loc>{loc}</loc>\n"
            f"    <lastmod>{lastmod}</lastmod>\n"
            f"    <changefreq>monthly</changefreq>\n"
            f"    <priority>0.6</priority>\n"
            f"  </url>"
        )

    body = "\n".join(urls)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{body}\n"
        "</urlset>"
    )
