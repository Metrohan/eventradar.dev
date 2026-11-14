from datetime import datetime
import pytest
from sqlalchemy.exc import IntegrityError
from app.models.event import Event, EventSlugAlias
from app.utils.event_urls import slug_base


def make(db, **values):
    data = dict(
        title="İstanbul Python Atölyesi",
        date=datetime(2027, 5, 15),
        url="https://example.org/one",
        source="test",
    )
    data.update(values)
    e = Event(**data)
    db.add(e)
    db.commit()
    return e


def test_clean_slug_is_stable_and_collisions_have_suffix(test_db):
    a = make(test_db)
    b = make(test_db, url="https://example.org/two")
    assert a.slug == "istanbul-python-atolyesi-2027-05-15"
    assert b.slug == a.slug + "-2"
    a.title = "Changed"
    a.date = datetime(2028, 1, 1)
    test_db.commit()
    assert a.slug == "istanbul-python-atolyesi-2027-05-15"
    assert slug_base("Çığ Şöleni", None) == "cig-soleni"


def test_alias_and_legacy_are_one_hop(client, test_db):
    e = make(test_db, slug="old-uuid")
    e.slug = "new-clean"
    test_db.commit()
    response = client.get("/events/old-uuid", follow_redirects=False)
    assert (
        response.status_code == 301
        and response.headers["location"] == "/events/new-clean"
    )
    assert (
        client.get(f"/etkinlik/{e.id}", follow_redirects=False).headers["location"]
        == "/events/new-clean"
    )
    assert client.get("/events/new-clean").status_code == 200
    e.is_active = False
    e.deactivation_reason = "manual"
    test_db.commit()
    assert client.get("/events/old-uuid").status_code == 404
    assert client.get("/events/new-clean").status_code == 404


def test_historical_alias_cannot_be_stolen(test_db):
    e = make(test_db, slug="reserved")
    e.slug = "renamed"
    test_db.commit()
    with pytest.raises(IntegrityError):
        make(test_db, slug="reserved", url="https://example.org/steal")
    test_db.rollback()
    assert (
        test_db.query(EventSlugAlias).filter_by(slug="reserved").one().event_id == e.id
    )


def test_new_default_respects_historical_reservation(test_db):
    old = make(test_db, slug="istanbul-python-atolyesi-2027-05-15")
    old.slug = "new-place"
    test_db.commit()
    fresh = make(test_db, url="https://example.org/fresh")
    assert fresh.slug == "istanbul-python-atolyesi-2027-05-15-2"


def test_date_unknown_gets_title_only(test_db):
    assert make(test_db, date=None).slug == "istanbul-python-atolyesi"


def test_manifest_apply_and_rollback_remain_one_hop(client, test_db):
    from scripts.review_event_slugs import plan_slugs, apply_routes

    e = make(test_db, slug="old-random", slug_version=1)
    changes = plan_slugs(
        test_db.query(Event).all(), test_db.query(EventSlugAlias).all()
    )
    assert changes[0]["old"] == "old-random"
    assert e.slug == "old-random"
    apply_routes(test_db, changes)
    canonical = e.slug
    assert (
        client.get("/events/old-random", follow_redirects=False).headers["location"]
        == f"/events/{canonical}"
    )
    apply_routes(test_db, changes, rollback=True)
    assert (
        client.get(f"/events/{canonical}", follow_redirects=False).headers["location"]
        == "/events/old-random"
    )
    assert client.get("/events/old-random").status_code == 200


def test_stale_manifest_does_not_change_any_routes(test_db):
    from scripts.review_event_slugs import plan_slugs, apply_routes

    e = make(test_db, slug="old-stale", slug_version=1)
    changes = plan_slugs([e], test_db.query(EventSlugAlias).all())
    e.title = "New title"
    test_db.commit()
    with pytest.raises(ValueError, match="snapshot changed"):
        apply_routes(test_db, changes)
    assert e.slug == "old-stale"


def test_repeated_preview_never_renames_a_clean_canonical(test_db):
    from scripts.review_event_slugs import plan_slugs, apply_routes

    fresh = make(test_db)
    assert fresh.slug_version == 2
    fresh.title = "Changed title"
    fresh.date = datetime(2028, 2, 1)
    test_db.commit()
    assert not plan_slugs([fresh], test_db.query(EventSlugAlias).all())
    legacy = make(
        test_db, slug="legacy-old", slug_version=1, url="https://example.org/legacy"
    )
    changes = plan_slugs([legacy], test_db.query(EventSlugAlias).all())
    apply_routes(test_db, changes)
    canonical = legacy.slug
    legacy.title = "Another title"
    test_db.commit()
    assert legacy.slug_version == 2
    assert not plan_slugs([legacy], test_db.query(EventSlugAlias).all())
    assert legacy.slug == canonical
