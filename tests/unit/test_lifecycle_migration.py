"""Exercise the additive revision against a legacy table, not create_all."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import create_engine, inspect, text


def test_lifecycle_revision_preserves_legacy_rows_in_both_directions():
    path = (
        Path(__file__).resolve().parents[2]
        / "alembic/versions/a2b3c4d5e6f7_add_event_deactivation_reason.py"
    )
    spec = spec_from_file_location("lifecycle_revision", path)
    revision = module_from_spec(spec)
    spec.loader.exec_module(revision)
    engine = create_engine("sqlite:///:memory:")
    with engine.begin() as connection:
        connection.execute(
            text(
                "CREATE TABLE events (id INTEGER PRIMARY KEY, title VARCHAR(500), is_active BOOLEAN)"
            )
        )
        connection.execute(
            text("INSERT INTO events VALUES (1, 'Legacy hidden event', 0)")
        )
        with Operations.context(MigrationContext.configure(connection)):
            revision.upgrade()
            row = connection.execute(
                text("SELECT title, is_active, deactivation_reason FROM events")
            ).one()
            assert tuple(row) == ("Legacy hidden event", 0, None)
            revision.downgrade()
        assert "deactivation_reason" not in {
            column["name"] for column in inspect(connection).get_columns("events")
        }
        assert connection.execute(
            text("SELECT title, is_active FROM events")
        ).one() == ("Legacy hidden event", 0)
    engine.dispose()
