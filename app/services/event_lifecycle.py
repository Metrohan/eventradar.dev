"""Event dates are Istanbul wall-clock values; visibility lasts through that day."""

from sqlalchemy import or_

from ..models.event import Event
from ..utils.event_dates import day_start


def visible_event_filter():
    return (
        Event.is_active.is_(True),
        or_(Event.date.is_(None), Event.date >= day_start()),
    )


def history_event_filter():
    # Manual and legacy-unknown hides must never become public via the history toggle.
    return or_(Event.is_active.is_(True), Event.deactivation_reason == "past")
