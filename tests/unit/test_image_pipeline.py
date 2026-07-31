import io
from unittest.mock import Mock, patch

import pytest
import requests
from PIL import Image

from app.services import image_pipeline


def _make_image_bytes(width=800, height=400, fmt="PNG"):
    img = Image.new("RGB", (width, height), color=(255, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    return buf.getvalue()


def _fake_response(
    body: bytes,
    status_code=200,
    content_type="image/png",
    chunk_size=65536,
):
    resp = Mock()
    resp.status_code = status_code
    resp.headers = {"Content-Type": content_type, "Content-Length": str(len(body))}

    def iter_content(chunk_size=chunk_size):
        for i in range(0, len(body), chunk_size):
            yield body[i : i + chunk_size]

    resp.iter_content = iter_content
    resp.__enter__ = Mock(return_value=resp)
    resp.__exit__ = Mock(return_value=False)
    return resp


# --- URL validation (allowlist + SSRF) ---------------------------------


def test_rejects_non_https_scheme():
    with pytest.raises(image_pipeline.ImageRejected, match="scheme"):
        image_pipeline._validate_url("http://coderspace.io/img.png")


def test_rejects_host_not_in_allowlist():
    with pytest.raises(image_pipeline.ImageRejected, match="allowlist"):
        image_pipeline._validate_url("https://evil.example.com/img.png")


def test_allows_known_source_subdomain():
    # learn.pupilica.com must match the "pupilica.com" suffix entry.
    assert image_pipeline._host_allowed("learn.pupilica.com") is True
    assert image_pipeline._host_allowed("pupilica.com.evil.com") is False


@patch("app.services.image_pipeline.socket.getaddrinfo")
def test_rejects_host_resolving_to_private_ip(mock_getaddrinfo):
    mock_getaddrinfo.return_value = [(2, 1, 6, "", ("10.0.0.5", 0))]
    with pytest.raises(image_pipeline.ImageRejected, match="non-public"):
        image_pipeline._validate_url("https://coderspace.io/img.png")


@patch("app.services.image_pipeline.socket.getaddrinfo")
def test_rejects_host_resolving_to_loopback(mock_getaddrinfo):
    mock_getaddrinfo.return_value = [(2, 1, 6, "", ("127.0.0.1", 0))]
    with pytest.raises(image_pipeline.ImageRejected, match="non-public"):
        image_pipeline._validate_url("https://coderspace.io/img.png")


@patch("app.services.image_pipeline.socket.getaddrinfo")
def test_allows_host_resolving_to_public_ip(mock_getaddrinfo):
    mock_getaddrinfo.return_value = [(2, 1, 6, "", ("93.184.216.34", 0))]
    image_pipeline._validate_url("https://coderspace.io/img.png")  # no raise


# --- resize ---------------------------------------------------------------


def test_resize_produces_400x200_webp():
    raw = _make_image_bytes(800, 400)
    out = image_pipeline._resize_to_webp(raw)
    with Image.open(io.BytesIO(out)) as img:
        assert img.format == "WEBP"
        assert img.size == (400, 200)


def test_resize_cover_crops_non_matching_aspect_ratio():
    # Tall source image; cover-crop should still land on exactly 400x200.
    raw = _make_image_bytes(300, 900)
    out = image_pipeline._resize_to_webp(raw)
    with Image.open(io.BytesIO(out)) as img:
        assert img.size == (400, 200)


# --- ensure_thumbnail: end-to-end + caching + fallback --------------------


@patch("app.services.image_pipeline.socket.getaddrinfo")
@patch("app.services.image_pipeline.requests.get")
def test_ensure_thumbnail_generates_and_caches(mock_get, mock_getaddrinfo, tmp_path):
    mock_getaddrinfo.return_value = [(2, 1, 6, "", ("93.184.216.34", 0))]
    mock_get.return_value = _fake_response(_make_image_bytes())

    url = "https://coderspace.io/events/foo.png"
    result1 = image_pipeline.ensure_thumbnail(url, tmp_path, "/media/thumbnails")
    assert result1 is not None
    assert result1.startswith("/media/thumbnails/")
    assert mock_get.call_count == 1

    cached_file = tmp_path / result1.rsplit("/", 1)[-1]
    assert cached_file.exists()

    # Second call for the same URL must be served from cache, no re-fetch.
    result2 = image_pipeline.ensure_thumbnail(url, tmp_path, "/media/thumbnails")
    assert result2 == result1
    assert mock_get.call_count == 1


@patch("app.services.image_pipeline.socket.getaddrinfo")
@patch("app.services.image_pipeline.requests.get")
def test_cache_invalidates_when_source_url_changes(
    mock_get, mock_getaddrinfo, tmp_path
):
    mock_getaddrinfo.return_value = [(2, 1, 6, "", ("93.184.216.34", 0))]
    mock_get.return_value = _fake_response(_make_image_bytes())

    url_a = "https://coderspace.io/events/a.png"
    url_b = "https://coderspace.io/events/b.png"

    result_a = image_pipeline.ensure_thumbnail(url_a, tmp_path, "/media/thumbnails")
    result_b = image_pipeline.ensure_thumbnail(url_b, tmp_path, "/media/thumbnails")

    assert result_a != result_b
    assert mock_get.call_count == 2


def test_ensure_thumbnail_returns_none_for_missing_url(tmp_path):
    assert image_pipeline.ensure_thumbnail(None, tmp_path, "/media/thumbnails") is None
    assert image_pipeline.ensure_thumbnail("", tmp_path, "/media/thumbnails") is None


def test_ensure_thumbnail_falls_back_on_disallowed_host(tmp_path):
    result = image_pipeline.ensure_thumbnail(
        "https://evil.example.com/img.png", tmp_path, "/media/thumbnails"
    )
    assert result is None
    assert list(tmp_path.iterdir()) == []


@patch("app.services.image_pipeline.socket.getaddrinfo")
@patch("app.services.image_pipeline.requests.get")
def test_ensure_thumbnail_falls_back_on_oversized_body(
    mock_get, mock_getaddrinfo, tmp_path, monkeypatch
):
    monkeypatch.setattr(image_pipeline, "MAX_IMAGE_BYTES", 100)
    mock_getaddrinfo.return_value = [(2, 1, 6, "", ("93.184.216.34", 0))]
    mock_get.return_value = _fake_response(_make_image_bytes(), chunk_size=16)

    result = image_pipeline.ensure_thumbnail(
        "https://coderspace.io/events/big.png", tmp_path, "/media/thumbnails"
    )
    assert result is None


@patch("app.services.image_pipeline.socket.getaddrinfo")
@patch("app.services.image_pipeline.requests.get")
def test_ensure_thumbnail_falls_back_on_non_image_content_type(
    mock_get, mock_getaddrinfo, tmp_path
):
    mock_getaddrinfo.return_value = [(2, 1, 6, "", ("93.184.216.34", 0))]
    mock_get.return_value = _fake_response(
        b"<html>not an image</html>", content_type="text/html"
    )

    result = image_pipeline.ensure_thumbnail(
        "https://coderspace.io/events/oops.html", tmp_path, "/media/thumbnails"
    )
    assert result is None


@patch("app.services.image_pipeline.socket.getaddrinfo")
@patch("app.services.image_pipeline.requests.get")
def test_ensure_thumbnail_falls_back_when_source_unreachable(
    mock_get, mock_getaddrinfo, tmp_path
):
    mock_getaddrinfo.return_value = [(2, 1, 6, "", ("93.184.216.34", 0))]
    mock_get.side_effect = requests.ConnectionError("boom")

    result = image_pipeline.ensure_thumbnail(
        "https://coderspace.io/events/down.png", tmp_path, "/media/thumbnails"
    )
    assert result is None


@patch("app.services.image_pipeline.socket.getaddrinfo")
@patch("app.services.image_pipeline.requests.get")
def test_ensure_thumbnail_falls_back_on_corrupt_image_bytes(
    mock_get, mock_getaddrinfo, tmp_path
):
    mock_getaddrinfo.return_value = [(2, 1, 6, "", ("93.184.216.34", 0))]
    mock_get.return_value = _fake_response(
        b"not actually an image", content_type="image/png"
    )

    result = image_pipeline.ensure_thumbnail(
        "https://coderspace.io/events/corrupt.png", tmp_path, "/media/thumbnails"
    )
    assert result is None
