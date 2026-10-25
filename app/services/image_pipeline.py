"""Scrape-time event card generation: render a canonical 400x200 WebP from an
event's own facts (title, date, location, source name) and cache it on local
disk. No third-party image is ever fetched, stored or shown.

See docs/adr/0006-generated-event-cards.md (supersedes the fetch/resize step
of docs/adr/0005-scrape-time-image-resize.md).
"""

from __future__ import annotations

import colorsys
import hashlib
import io
import logging
import os
from datetime import datetime
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

THUMBNAIL_WIDTH = 400
THUMBNAIL_HEIGHT = 200

# Draw at 2x and downscale: cheap anti-aliasing for small text.
_SCALE = 2
_MARGIN = 20 * _SCALE

# Scraped text is untrusted and unbounded (location is a Text column); cap it
# before measuring/hashing so _fit's per-character loop stays cheap.
_MAX_TEXT_CHARS = 300

# Bump to regenerate every card after a design change (it is part of the cache key).
_RENDER_VERSION = "v1"

# Liberation Sans covers Turkish glyphs and is already in the prod image
# (fonts-liberation, installed for Chrome). Paths: Debian first, then Arch/dev.
_FONT_DIRS = (
    "/usr/share/fonts/truetype/liberation",
    "/usr/share/fonts/liberation",
    "/usr/share/fonts/TTF",
)
_FONT_FILES = {
    True: ("LiberationSans-Bold.ttf", "DejaVuSans-Bold.ttf"),
    False: ("LiberationSans-Regular.ttf", "DejaVuSans.ttf"),
}

_MONTHS_TR = ("Oca", "Şub", "Mar", "Nis", "May", "Haz",
              "Tem", "Ağu", "Eyl", "Eki", "Kas", "Ara")  # fmt: skip


class CardRenderError(Exception):
    """No usable font was found, so no card can be drawn."""


@lru_cache(maxsize=None)
def _font(bold: bool, size: int) -> ImageFont.FreeTypeFont:
    for directory in _FONT_DIRS:
        for name in _FONT_FILES[bold]:
            try:
                return ImageFont.truetype(str(Path(directory) / name), size)
            except OSError:
                continue
    raise CardRenderError("no Liberation Sans/DejaVu Sans font installed")


def _format_date(value: datetime | None) -> str | None:
    if value is None:
        return None
    return f"{value.day} {_MONTHS_TR[value.month - 1]} {value.year}"


def _fit(draw: ImageDraw.ImageDraw, text: str, font, max_width: int) -> str:
    """Single line, ellipsised to max_width."""
    if draw.textlength(text, font=font) <= max_width:
        return text
    while text and draw.textlength(text + "…", font=font) > max_width:
        text = text[:-1]
    return text.rstrip() + "…"


def _wrap(
    draw: ImageDraw.ImageDraw, text: str, font, max_width: int, max_lines: int
) -> list[str]:
    """Greedy word wrap; the last allowed line is ellipsised if text remains."""
    lines: list[str] = []
    current = ""
    for word in text.split():
        candidate = f"{current} {word}".strip()
        if current and draw.textlength(candidate, font=font) > max_width:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] += "…"
    return [_fit(draw, line, font, max_width) for line in lines]


def _accent_hue(source: str) -> float:
    digest = hashlib.sha256(source.encode("utf-8")).digest()
    return int.from_bytes(digest[:2], "big") % 360 / 360


def _render(
    title: str, date_text: str | None, location: str | None, source: str
) -> bytes:
    width, height = THUMBNAIL_WIDTH * _SCALE, THUMBNAIL_HEIGHT * _SCALE
    hue = _accent_hue(source)
    bg = tuple(int(c * 255) for c in colorsys.hls_to_rgb(hue, 0.20, 0.45))
    accent = tuple(int(c * 255) for c in colorsys.hls_to_rgb(hue, 0.70, 0.55))

    img = Image.new("RGB", (width, height), bg)
    draw = ImageDraw.Draw(img)
    max_width = width - 2 * _MARGIN

    draw.rectangle((0, 0, 6 * _SCALE, height), fill=accent)

    draw.text(
        (_MARGIN, _MARGIN),
        _fit(draw, source.upper(), _font(True, 13 * _SCALE), max_width),
        font=_font(True, 13 * _SCALE),
        fill=accent,
    )

    title_font = _font(True, 22 * _SCALE)
    y = _MARGIN + 30 * _SCALE
    for line in _wrap(draw, title, title_font, max_width, max_lines=3):
        draw.text((_MARGIN, y), line, font=title_font, fill=(255, 255, 255))
        y += 27 * _SCALE

    bottom: list[tuple[str, bool]] = []
    if date_text:
        bottom.append((date_text, True))
    if location:
        bottom.append((" ".join(location.split()), False))
    line_height = 19 * _SCALE
    y = height - _MARGIN - len(bottom) * line_height + 2 * _SCALE
    for text, bold in bottom:
        font = _font(bold, 14 * _SCALE)
        draw.text(
            (_MARGIN, y),
            _fit(draw, text, font, max_width),
            font=font,
            fill=(235, 235, 240) if bold else (200, 200, 210),
        )
        y += line_height

    img = img.resize((THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT), Image.Resampling.LANCZOS)
    out = io.BytesIO()
    img.save(out, format="WEBP", quality=85, method=6)
    return out.getvalue()


def _cache_key(
    title: str, date_text: str | None, location: str | None, source: str
) -> str:
    raw = "\x1f".join((_RENDER_VERSION, title, date_text or "", location or "", source))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


def card_public_url(
    title: str,
    date: datetime | None,
    location: str | None,
    source: str,
    public_prefix: str,
) -> str | None:
    """Public URL the card for these facts has (or will have); None for a blank title."""
    prepared = _prepare(title, date, location, source)
    if prepared is None:
        return None
    return f"{public_prefix.rstrip('/')}/{_cache_key(*prepared)}.webp"


def _prepare(
    title: str, date: datetime | None, location: str | None, source: str
) -> tuple[str, str | None, str | None, str] | None:
    """Trim/cap untrusted scraped text; the result feeds both the cache key and _render."""
    title = title.strip()[:_MAX_TEXT_CHARS]
    if not title:
        return None
    return (
        title,
        _format_date(date),
        location[:_MAX_TEXT_CHARS] if location else location,
        source[:_MAX_TEXT_CHARS],
    )


def ensure_card(
    title: str,
    date: datetime | None,
    location: str | None,
    source: str,
    thumbnail_dir: Path,
    public_prefix: str,
) -> str | None:
    """Return the public URL of a cached/generated 400x200 WebP card for the
    event, or None if it could not be drawn.

    Never raises: any failure is logged and treated as "no thumbnail", letting
    the frontend fall back to the static placeholder.
    """
    prepared = _prepare(title, date, location, source)
    if prepared is None:
        return None

    filename = f"{_cache_key(*prepared)}.webp"
    dest = thumbnail_dir / filename
    public_url = f"{public_prefix.rstrip('/')}/{filename}"

    if dest.exists():
        return public_url

    try:
        webp_bytes = _render(*prepared)
        thumbnail_dir.mkdir(parents=True, exist_ok=True)
        tmp_dest = dest.with_name(
            f"{dest.name}.{os.getpid()}.tmp"
        )  # unique per process
        tmp_dest.write_bytes(webp_bytes)
        tmp_dest.replace(dest)
    except CardRenderError as exc:
        logger.warning("Event card skipped: %s", exc)
        return None
    except Exception:
        logger.exception("Unexpected error rendering event card for %r", title)
        return None
    return public_url
