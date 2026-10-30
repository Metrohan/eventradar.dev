"""Public HTML pages: identical content for people and crawlers, no JS required."""

import html
import re
from urllib.parse import quote

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..models.event import Event
from ..models.tag import Tag
from ..services.location_normalizer import CITY_NAMES
from ..services.event_lifecycle import history_event_filter, visible_event_filter
from ..services.seo_head import _event_meta, _render, _Meta, _ld_json, SITE_URL
from ..utils.event_dates import day_start, local_now
from ..utils.event_urls import event_path

router = APIRouter(include_in_schema=False)


def esc(value):
    return html.escape(str(value or ""), quote=True)


def page(head, body, status=200):
    organization = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "TechEventRadar",
        "url": SITE_URL,
        "logo": SITE_URL + "/pwa-icon-512.png",
    }
    return HTMLResponse(
        '<!doctype html><html lang="tr"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        + head
        + '<script type="application/ld+json">'
        + _ld_json(organization)
        + "</script>"
        "<style>body{font:18px/1.7 system-ui;max-width:850px;margin:40px auto;padding:0 20px;"
        "color:#e2e8f0;background:#0f172a}a{color:#38bdf8}h1{line-height:1.25}"
        "p{white-space:pre-line}dt{font-weight:bold}dd{margin:0 0 16px}li{margin:12px 0}</style>"
        '</head><body><header><a href="/">TechEventRadar</a> · '
        '<a href="/kategoriler">Kategoriler</a> · <a href="/sehirler">Şehirler</a></header>'
        "<main>" + body + "</main></body></html>",
        status_code=status,
    )


def missing():
    return page(
        _render(
            _Meta("Etkinlik bulunamadı | TechEventRadar", "İçerik bulunamadı.", None)
        ),
        '<h1>Etkinlik bulunamadı</h1><a href="/">Etkinlikleri keşfet</a>',
        404,
    )


@router.get("/etkinlik/{event_id:int}")
def legacy_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id, history_event_filter()).first()
    return RedirectResponse(event_path(event), status_code=301) if event else missing()


@router.get("/events/{slug}")
def event_detail(slug: str, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.slug == slug, history_event_filter()).first()
    if not event:
        return missing()
    past = event.date is not None and event.date < day_start()
    meta = _event_meta(event)
    if past or not event.is_active:
        meta.path = None
        meta.json_ld = []
    fields = [
        ("Etkinlik tarihi", event.date),
        ("Son başvuru", event.application_deadline),
    ]
    dates = "".join(
        "<dt>"
        + label
        + "</dt><dd>"
        + (
            '<time datetime="'
            + esc(value.isoformat())
            + '">'
            + esc(value.strftime("%d.%m.%Y %H:%M"))
            + "</time>"
            if value
            else "Belirtilmedi"
        )
        + "</dd>"
        for label, value in fields
    )
    status = "<p>Etkinlik sona erdi</p>" if past else ""
    deadline = event.application_deadline
    # Midnight is the established date-only convention; explicit times expire
    # precisely. The source model cannot distinguish explicit midnight yet.
    deadline_limit = (
        local_now()
        if deadline and deadline.time().isoformat() != "00:00:00"
        else day_start()
    )
    if deadline and deadline < deadline_limit:
        status += "<p>Başvurular kapandı</p>"
    safe_url = str(event.url) if re.match(r"^https?://", str(event.url), re.I) else "/"
    body = (
        "<h1>"
        + esc(event.title)
        + "</h1>"
        + status
        + "<dl>"
        + dates
        + "<dt>Konum</dt><dd>"
        + esc(event.location or "Belirtilmedi")
        + "</dd>"
        "<dt>Kaynak</dt><dd>"
        + esc(event.source)
        + "</dd></dl><p>"
        + esc(event.description)
        + '</p><a rel="noopener noreferrer" href="'
        + esc(safe_url)
        + '">Kaynak sayfasını görüntüle</a>'
    )
    card = str(event.thumbnail_url or "")
    if card.startswith("/media/thumbnails/"):
        body = (
            '<img src="'
            + esc(card)
            + '" alt="" width="400" height="200" style="max-width:100%;height:auto">'
            + body
        )
    share_url = quote(SITE_URL + event_path(event), safe="")
    body += (
        '<nav aria-label="Paylaş"><p>Paylaş: '
        '<a rel="noopener noreferrer" href="https://wa.me/?text='
        + share_url
        + '">WhatsApp</a> · '
        '<a rel="noopener noreferrer" href="https://t.me/share/url?url='
        + share_url
        + '">Telegram</a> · '
        '<a href="mailto:?body=' + share_url + '">E-posta</a></p></nav>'
    )
    return page(_render(meta), body)


CITIES = CITY_NAMES


def listing(path, title, events):
    body = (
        "<h1>"
        + esc(title)
        + "</h1><ul>"
        + "".join(
            '<li><a href="'
            + esc(event_path(event))
            + '">'
            + esc(event.title)
            + "</a></li>"
            for event in events
        )
        + "</ul>"
    )
    if not events:
        body += "<p>Şu anda güncel etkinlik bulunmuyor.</p>"
    return page(
        _render(_Meta(title + " | TechEventRadar", title, path if events else None)),
        body,
    )


@router.get("/kategoriler")
def categories(db: Session = Depends(get_db)):
    tags = db.query(Tag).order_by(Tag.name).all()
    body = (
        "<h1>Kategoriler</h1><ul>"
        + "".join(
            '<li><a href="/kategoriler/'
            + esc(tag.name)
            + '">'
            + esc(tag.label)
            + "</a></li>"
            for tag in tags
            if re.fullmatch(r"[a-z0-9-]+", str(tag.name))
        )
        + "</ul>"
    )
    return page(
        _render(
            _Meta(
                "Etkinlik kategorileri | TechEventRadar",
                "Teknoloji etkinlik kategorileri.",
                "/kategoriler",
            )
        ),
        body,
    )


@router.get("/kategoriler/{category}")
def category_page(category: str, db: Session = Depends(get_db)):
    tag = db.query(Tag).filter(Tag.name == category).first()
    if not tag:
        return missing()
    events = (
        db.query(Event)
        .filter(*visible_event_filter(), Event.tags.any(Tag.id == tag.id))
        .order_by(Event.date, Event.id)
        .all()
    )
    return listing("/kategoriler/" + category, str(tag.label) + " etkinlikleri", events)


@router.get("/sehirler")
def cities():
    body = (
        "<h1>Şehirler</h1><ul>"
        + "".join(
            '<li><a href="/sehirler/' + slug + '">' + city + "</a></li>"
            for slug, city in CITIES.items()
        )
        + "</ul>"
    )
    return page(
        _render(
            _Meta(
                "Şehirlere göre etkinlikler | TechEventRadar",
                "Şehrindeki teknoloji etkinlikleri.",
                "/sehirler",
            )
        ),
        body,
    )


@router.get("/sehirler/{city}")
def city_page(city: str, db: Session = Depends(get_db)):
    name = CITIES.get(city)
    if name is None:
        return missing()
    # Exact normalized city values only: do not infer a venue's city or include online events.
    events = (
        db.query(Event)
        .filter(*visible_event_filter(), Event.location == name)
        .order_by(Event.date, Event.id)
        .all()
    )
    return listing("/sehirler/" + city, name + " etkinlikleri", events)
