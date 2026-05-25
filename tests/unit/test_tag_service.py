import os
os.environ.setdefault("ALLOW_INSECURE_DEFAULTS", "true")
os.environ.setdefault("SECRET_KEY", "test-secret-key-that-is-at-least-32-chars")
os.environ.setdefault("ADMIN_USERNAME", "testadmin")
os.environ.setdefault("ADMIN_PASSWORD", "testpassword")

import pytest
from app.services.tag_service import classify_event, seed_tags
from app.models.tag import Tag


def test_classify_hackathon():
    assert "hackathon" in classify_event("İstanbul Hackathon 2026", None)


def test_classify_seminer():
    assert "seminer" in classify_event("Python Webinar Başlıyor", "Online etkinlik")


def test_classify_atolye():
    assert "atolye" in classify_event("React Workshop İstanbul", None)


def test_classify_konferans():
    assert "konferans" in classify_event("Tech Summit Ankara", "Yıllık konferans")


def test_classify_bootcamp():
    assert "bootcamp" in classify_event("Fullstack Bootcamp", None)


def test_classify_multi():
    result = classify_event("Hackathon & Workshop", None)
    assert "hackathon" in result
    assert "atolye" in result


def test_classify_fallback_to_diger():
    result = classify_event("Tanışma Toplantısı", None)
    assert result == ["diger"]


def test_classify_case_insensitive():
    assert "hackathon" in classify_event("HACKATHON FİNALİ", None)


def test_seed_tags_creates_six_tags(test_db):
    seed_tags(test_db)
    tags = test_db.query(Tag).all()
    assert len(tags) == 6
    names = {t.name for t in tags}
    assert names == {"hackathon", "seminer", "atolye", "konferans", "bootcamp", "diger"}


def test_seed_tags_is_idempotent(test_db):
    seed_tags(test_db)
    seed_tags(test_db)  # second call must not raise or duplicate
    assert test_db.query(Tag).count() == 6
