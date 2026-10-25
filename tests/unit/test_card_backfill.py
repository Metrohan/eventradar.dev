from datetime import datetime
from pathlib import Path

import pytest

from app.models.event import Event
from app.services import image_pipeline
from app.services.card_backfill import backfill_cards

PREFIX = "/media/thumbnails"


def _event(
    db,
    title="Hackathon",
    url="https://example.com/h",
    thumb="/media/thumbnails/old.webp",
):
    event = Event(
        title=title,
        url=url,
        source="Youthall",
        location="İstanbul",
        date=datetime(2099, 1, 1),
        thumbnail_url=thumb,
    )
    db.add(event)
    db.commit()
    return event


@pytest.fixture
def dirs(tmp_path):
    served = tmp_path / "thumbnails"
    served.mkdir()
    (served / "old.webp").write_bytes(b"copied third-party image")
    return served, tmp_path / "archive"


def test_dry_run_reports_but_changes_nothing(test_db, dirs):
    served, _ = dirs
    event = _event(test_db)

    report = backfill_cards(test_db, served, PREFIX)

    assert (report.events_total, report.rows_to_change) == (1, 1)
    assert [f.name for f in report.orphan_files] == ["old.webp"]
    assert event.thumbnail_url == "/media/thumbnails/old.webp"
    assert sorted(f.name for f in served.iterdir()) == ["old.webp"]


def test_apply_points_rows_at_cards_and_archives_old_files(test_db, dirs):
    served, archive = dirs
    event = _event(test_db)

    report = backfill_cards(test_db, served, PREFIX, archive_dir=archive, apply=True)

    expected = image_pipeline.card_public_url(
        "Hackathon", datetime(2099, 1, 1), "İstanbul", "Youthall", PREFIX
    )
    assert event.thumbnail_url == expected
    assert (served / expected.rsplit("/", 1)[1]).exists()
    assert not (served / "old.webp").exists()
    assert (archive / "old.webp").read_bytes() == b"copied third-party image"
    assert report.archived_to == archive


def test_apply_is_idempotent(test_db, dirs):
    served, archive = dirs
    _event(test_db)
    backfill_cards(test_db, served, PREFIX, archive_dir=archive, apply=True)

    report = backfill_cards(test_db, served, PREFIX, archive_dir=archive, apply=True)

    assert report.rows_to_change == 0
    assert report.orphan_files == []


def test_blank_title_row_loses_old_image_and_gets_no_card(test_db, dirs):
    served, archive = dirs
    event = _event(test_db, title="   ")

    report = backfill_cards(test_db, served, PREFIX, archive_dir=archive, apply=True)

    assert event.thumbnail_url is None
    assert report.rows_without_card == 1
    assert (archive / "old.webp").exists()


def test_symlinks_are_never_moved(test_db, dirs):
    served, archive = dirs
    outside = served.parent / "precious.txt"
    outside.write_text("keep")
    (served / "link.webp").symlink_to(outside)
    _event(test_db)

    backfill_cards(test_db, served, PREFIX, archive_dir=archive, apply=True)

    assert (served / "link.webp").is_symlink()
    assert outside.read_text() == "keep"


def test_apply_requires_archive_dir_outside_served_dir(test_db, dirs):
    served, _ = dirs
    with pytest.raises(ValueError):
        backfill_cards(test_db, served, PREFIX, apply=True)
    with pytest.raises(ValueError):
        backfill_cards(test_db, served, PREFIX, archive_dir=served / "old", apply=True)
