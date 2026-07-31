"""Scrape-time thumbnail generation: fetch a source event image, validate it
against SSRF/size rules, resize it to a canonical 400x200 WebP, and cache the
result on local disk keyed by the source URL.

See docs/adr/0005-scrape-time-image-resize.md for the architecture decision.
"""

from __future__ import annotations

import hashlib
import ipaddress
import logging
import socket
from pathlib import Path
from urllib.parse import urlparse

import requests
from PIL import Image, UnidentifiedImageError

logger = logging.getLogger(__name__)

# Thumbnail dimensions mandated by issue #76's acceptance criteria.
THUMBNAIL_WIDTH = 400
THUMBNAIL_HEIGHT = 200

# Generous margin over the largest source image observed in production
# (~2.3 MB) while still bounding worst-case memory/disk use per fetch.
MAX_IMAGE_BYTES = 8 * 1024 * 1024

FETCH_TIMEOUT_SECONDS = 10

# Coarse allowlist derived from the domains scrapers actually construct
# image URLs from (see app/scrapers/*.py) plus the third-party CDNs
# identified in issue #76's PageSpeed audit (Webflow, Framer). Matched by
# suffix, so subdomains (e.g. learn.pupilica.com) are covered automatically.
# This is a coarse filter, not the primary defense — IP-based SSRF
# validation below is what actually blocks internal targets. Extend this
# set when a legitimate source's thumbnail is silently skipped.
ALLOWED_IMAGE_HOST_SUFFIXES = frozenset(
    {
        "anbeankampus.co",
        "ibb.gov.tr",
        "coderspace.io",
        "kodluyoruz.org",
        "komunite.com.tr",
        "pupilica.com",
        "tech.istanbul",
        "akbankgenclikakademisi.com",
        "patika.dev",
        "techcareer.net",
        "youthall.com",
        "website-files.com",
        "framerusercontent.com",
    }
)


class ImageRejected(Exception):
    """Source image failed a validation rule (SSRF, size, format, host)."""


def _host_allowed(hostname: str) -> bool:
    hostname = hostname.lower()
    return any(
        hostname == suffix or hostname.endswith(f".{suffix}")
        for suffix in ALLOWED_IMAGE_HOST_SUFFIXES
    )


def _resolved_ips_are_public(hostname: str) -> bool:
    """Resolve hostname and reject if any address is a non-public target.

    Known limitation: this checks DNS at validation time, not at connection
    time, so it does not defend against DNS-rebinding attacks. Acceptable
    here because the host is additionally constrained by
    ALLOWED_IMAGE_HOST_SUFFIXES — an attacker would need to control DNS for
    an already-trusted source domain, which is a larger compromise than
    this pipeline can meaningfully defend against.
    """
    try:
        infos = socket.getaddrinfo(hostname, None)
    except socket.gaierror:
        return False

    for info in infos:
        raw_ip = info[4][0]
        ip = ipaddress.ip_address(raw_ip)
        if (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_multicast
            or ip.is_reserved
            or ip.is_unspecified
        ):
            return False
    return True


def _validate_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme != "https":
        raise ImageRejected(f"scheme not allowed: {parsed.scheme!r}")
    if not parsed.hostname:
        raise ImageRejected("missing hostname")
    if not _host_allowed(parsed.hostname):
        raise ImageRejected(f"host not in allowlist: {parsed.hostname}")
    if not _resolved_ips_are_public(parsed.hostname):
        raise ImageRejected(f"host resolves to a non-public address: {parsed.hostname}")


def _fetch_image_bytes(url: str) -> bytes:
    """Stream-download url, enforcing MAX_IMAGE_BYTES regardless of what
    (or whether) the server reports via Content-Length."""
    with requests.get(
        url,
        stream=True,
        timeout=FETCH_TIMEOUT_SECONDS,
        allow_redirects=False,
        headers={"User-Agent": "TechEventRadar-ImagePipeline/1.0"},
    ) as resp:
        if resp.status_code != 200:
            raise ImageRejected(f"unexpected status {resp.status_code}")

        content_type = resp.headers.get("Content-Type", "")
        if not content_type.startswith("image/"):
            raise ImageRejected(f"unexpected content-type: {content_type!r}")

        declared_length = resp.headers.get("Content-Length")
        if declared_length and int(declared_length) > MAX_IMAGE_BYTES:
            raise ImageRejected("declared Content-Length exceeds limit")

        chunks = []
        total = 0
        for chunk in resp.iter_content(chunk_size=65536):
            total += len(chunk)
            if total > MAX_IMAGE_BYTES:
                raise ImageRejected("body exceeded MAX_IMAGE_BYTES while streaming")
            chunks.append(chunk)
        return b"".join(chunks)


def _resize_to_webp(image_bytes: bytes) -> bytes:
    import io

    with Image.open(io.BytesIO(image_bytes)) as source:
        source.load()
        img: Image.Image = (
            source.convert("RGB") if source.mode not in ("RGB", "RGBA") else source
        )

        # Cover-crop to 400x200 so the source aspect ratio doesn't distort.
        target_ratio = THUMBNAIL_WIDTH / THUMBNAIL_HEIGHT
        src_ratio = img.width / img.height
        if src_ratio > target_ratio:
            new_width = int(img.height * target_ratio)
            offset = (img.width - new_width) // 2
            img = img.crop((offset, 0, offset + new_width, img.height))
        else:
            new_height = int(img.width / target_ratio)
            offset = (img.height - new_height) // 2
            img = img.crop((0, offset, img.width, offset + new_height))

        img = img.resize((THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT), Image.Resampling.LANCZOS)

        out = io.BytesIO()
        img.save(out, format="WEBP", quality=80, method=6)
        return out.getvalue()


def _cache_key(source_url: str) -> str:
    return hashlib.sha256(source_url.encode("utf-8")).hexdigest()[:24]


def ensure_thumbnail(
    source_url: str | None, thumbnail_dir: Path, public_prefix: str
) -> str | None:
    """Return the public URL of a cached/generated 400x200 WebP thumbnail
    for source_url, or None if the source is missing/invalid/unreachable.

    Never raises — any failure is logged and treated as "no thumbnail",
    letting callers fall back to the original image_url or a placeholder.
    """
    if not source_url:
        return None

    key = _cache_key(source_url)
    filename = f"{key}.webp"
    dest = thumbnail_dir / filename
    public_url = f"{public_prefix.rstrip('/')}/{filename}"

    if dest.exists():
        return public_url

    try:
        _validate_url(source_url)
        raw = _fetch_image_bytes(source_url)
        webp_bytes = _resize_to_webp(raw)
    except ImageRejected as exc:
        logger.info("Thumbnail skipped for %s: %s", source_url, exc)
        return None
    except UnidentifiedImageError:
        logger.info("Thumbnail skipped for %s: unrecognized image format", source_url)
        return None
    except requests.RequestException as exc:
        logger.info("Thumbnail fetch failed for %s: %s", source_url, exc)
        return None
    except Exception:
        logger.exception("Unexpected error generating thumbnail for %s", source_url)
        return None

    thumbnail_dir.mkdir(parents=True, exist_ok=True)
    tmp_dest = dest.with_suffix(".webp.tmp")
    tmp_dest.write_bytes(webp_bytes)
    tmp_dest.replace(dest)
    return public_url
