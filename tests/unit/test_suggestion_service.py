import os

os.environ.setdefault("ALLOW_INSECURE_DEFAULTS", "true")
os.environ.setdefault("SECRET_KEY", "test-secret-key-that-is-at-least-32-chars")
os.environ.setdefault("ADMIN_USERNAME", "testadmin")
os.environ.setdefault("ADMIN_PASSWORD", "testpassword")

import pytest
from app.services.suggestion_service import SuggestionService
from app.schemas.suggestion import SuggestionCreate


def _sug(**kwargs) -> SuggestionCreate:
    defaults = dict(
        suggestion_type="oneri",
        suggestion_title="Better search",
        suggestion_text="Add full-text search please",
    )
    defaults.update(kwargs)
    return SuggestionCreate(**defaults)


def test_create_and_get_suggestion(test_db):
    service = SuggestionService(test_db)
    created = service.create_suggestion(_sug())
    assert created.id is not None
    assert created.suggestion_title == "Better search"


def test_get_suggestions_returns_list(test_db):
    service = SuggestionService(test_db)
    service.create_suggestion(_sug(suggestion_title="A"))
    service.create_suggestion(_sug(suggestion_title="B"))
    items = service.get_suggestions()
    assert len(items) == 2


def test_get_suggestion_by_id(test_db):
    service = SuggestionService(test_db)
    created = service.create_suggestion(_sug())
    fetched = service.get_suggestion_by_id(created.id)
    assert fetched is not None
    assert fetched.id == created.id


def test_get_suggestion_by_id_not_found(test_db):
    service = SuggestionService(test_db)
    assert service.get_suggestion_by_id(9999) is None


def test_delete_suggestion(test_db):
    service = SuggestionService(test_db)
    created = service.create_suggestion(_sug())
    assert service.delete_suggestion(created.id) is True
    assert service.get_suggestion_by_id(created.id) is None


def test_delete_suggestion_not_found(test_db):
    service = SuggestionService(test_db)
    assert service.delete_suggestion(9999) is False
