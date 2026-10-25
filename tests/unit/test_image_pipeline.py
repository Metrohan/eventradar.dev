from datetime import datetime
from unittest.mock import patch

import pytest
from PIL import Image, ImageDraw

from app.services import image_pipeline

PREFIX = "/media/thumbnails"
WHEN = datetime(2026, 11, 7, 18, 30)


def _card(
    tmp_path, title="Hackathon 2026", date=WHEN, location="İstanbul", source="Youthall"
):
    return image_pipeline.ensure_card(title, date, location, source, tmp_path, PREFIX)


def test_format_date_uses_turkish_month_abbreviations():
    assert image_pipeline._format_date(datetime(2026, 8, 3)) == "3 Ağu 2026"
    assert image_pipeline._format_date(None) is None


def test_ensure_card_writes_400x200_webp_and_returns_public_url(tmp_path):
    url = _card(tmp_path)

    assert url.startswith(f"{PREFIX}/") and url.endswith(".webp")
    with Image.open(tmp_path / url.rsplit("/", 1)[1]) as img:
        assert img.format == "WEBP"
        assert img.size == (400, 200)


def test_ensure_card_is_cached_by_content(tmp_path):
    first = _card(tmp_path)
    with patch.object(image_pipeline, "_render") as render:
        assert _card(tmp_path) == first
    render.assert_not_called()


@pytest.mark.parametrize(
    "change",
    [
        {"title": "Başka Etkinlik"},
        {"date": datetime(2026, 11, 8)},
        {"location": "Ankara"},
        {"source": "Patika"},
    ],
)
def test_card_changes_when_any_shown_fact_changes(tmp_path, change):
    assert _card(tmp_path) != _card(tmp_path, **change)


@pytest.mark.parametrize("title", ["", "   "])
def test_ensure_card_returns_none_for_blank_title(tmp_path, title):
    assert _card(tmp_path, title=title) is None
    assert list(tmp_path.iterdir()) == []


def test_ensure_card_renders_without_date_and_location(tmp_path):
    assert _card(tmp_path, date=None, location=None) is not None


def test_ensure_card_handles_very_long_text_and_turkish_characters(tmp_path):
    url = _card(
        tmp_path,
        title="Çok Uzun Bir Yazılım Geliştirme Hackathonu " * 8,
        location="Şişli, Ümraniye Teknoloji Merkezi ve İstanbul Üniversitesi Kampüsü "
        * 4,
        source="Ğ" * 200,
    )

    assert url is not None
    with Image.open(tmp_path / url.rsplit("/", 1)[1]) as img:
        assert img.size == (400, 200)


def test_ensure_card_caps_huge_text_before_rendering(tmp_path):
    with patch.object(
        image_pipeline, "_render", wraps=image_pipeline._render
    ) as render:
        url = _card(
            tmp_path, title="x" * 100_000, location="y" * 100_000, source="z" * 100_000
        )

    assert url is not None
    title, _date, location, source = render.call_args.args
    cap = image_pipeline._MAX_TEXT_CHARS
    assert (len(title), len(location), len(source)) == (cap, cap, cap)


def test_ensure_card_returns_none_when_no_font_is_installed(tmp_path):
    with patch.object(
        image_pipeline, "_font", side_effect=image_pipeline.CardRenderError("no font")
    ):
        assert _card(tmp_path) is None
    assert list(tmp_path.iterdir()) == []


def test_ensure_card_returns_none_on_unexpected_error(tmp_path):
    with patch.object(image_pipeline, "_render", side_effect=RuntimeError("boom")):
        assert _card(tmp_path) is None


def test_wrap_truncates_to_max_lines_with_ellipsis():
    draw = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    font = image_pipeline._font(True, 44)

    lines = image_pipeline._wrap(draw, "kelime " * 60, font, 700, max_lines=3)

    assert len(lines) == 3
    assert lines[-1].endswith("…")
    assert all(draw.textlength(line, font=font) <= 700 for line in lines)


def test_wrap_keeps_short_text_on_one_line():
    draw = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    font = image_pipeline._font(True, 44)

    assert image_pipeline._wrap(draw, "Kısa başlık", font, 700, max_lines=3) == [
        "Kısa başlık"
    ]
