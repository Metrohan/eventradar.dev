"""One-off migration to ADR-0006: point every event at its generated card and
move the old copied thumbnail files out of the served directory.

Dry-run by default: nothing is written, rendered or moved unless apply=True.
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from pathlib import Path

from sqlalchemy.orm import Session

from ..models.event import Event
from . import image_pipeline


@dataclass
class BackfillReport:
    events_total: int = 0
    rows_to_change: int = 0
    rows_without_card: int = 0
    orphan_files: list[Path] = field(default_factory=list)
    archived_to: Path | None = None


def _filename(public_url: str | None) -> str | None:
    return public_url.rsplit("/", 1)[-1] if public_url else None


def backfill_cards(
    db: Session,
    thumbnail_dir: Path,
    public_prefix: str,
    archive_dir: Path | None = None,
    apply: bool = False,
) -> BackfillReport:
    """Re-point events at their cards; move files no event references to archive_dir.

    Orphans are moved (reversible), never deleted. archive_dir must be given with
    apply=True and must not be inside thumbnail_dir (which is served publicly).
    """
    if apply:
        if archive_dir is None:
            raise ValueError("apply=True requires archive_dir")
        if archive_dir.resolve().is_relative_to(thumbnail_dir.resolve()):
            raise ValueError("archive_dir must be outside the served thumbnail_dir")

    report = BackfillReport()
    referenced: set[str] = set()

    for event in db.query(Event).all():
        report.events_total += 1
        expected = image_pipeline.card_public_url(
            str(event.title),
            event.date,  # type: ignore[arg-type]
            event.location,  # type: ignore[arg-type]
            str(event.source),
            public_prefix,
        )
        if expected is None:
            report.rows_without_card += 1
        if event.thumbnail_url != expected:
            report.rows_to_change += 1
        if apply:
            if expected is not None:
                expected = image_pipeline.ensure_card(
                    str(event.title),
                    event.date,  # type: ignore[arg-type]
                    event.location,  # type: ignore[arg-type]
                    str(event.source),
                    thumbnail_dir,
                    public_prefix,
                )
            event.thumbnail_url = expected  # type: ignore[assignment]
        if expected:
            referenced.add(_filename(expected))  # type: ignore[arg-type]

    if apply:
        db.commit()

    # Regular files only; a symlink is never followed or moved.
    if thumbnail_dir.is_dir():
        report.orphan_files = sorted(
            f
            for f in thumbnail_dir.iterdir()
            if f.is_file() and not f.is_symlink() and f.name not in referenced
        )

    if apply and report.orphan_files:
        assert archive_dir is not None
        archive_dir.mkdir(parents=True, exist_ok=True)
        for f in report.orphan_files:
            shutil.move(str(f), str(archive_dir / f.name))
        report.archived_to = archive_dir

    return report
