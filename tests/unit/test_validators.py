import os

os.environ.setdefault("ALLOW_INSECURE_DEFAULTS", "true")
os.environ.setdefault("SECRET_KEY", "test-secret-key-that-is-at-least-32-chars")
os.environ.setdefault("ADMIN_USERNAME", "testadmin")
os.environ.setdefault("ADMIN_PASSWORD", "testpassword")

import pytest
from app.utils.validators import EventValidator


@pytest.fixture
def validator():
    return EventValidator()


@pytest.fixture
def valid_event():
    return {
        "title": "Python Bootcamp Istanbul",
        "url": "https://example.com/events/python-bootcamp",
        "source": "test",
        "description": "A great bootcamp",
        "image_url": "https://example.com/image.jpg",
        "location": "Istanbul",
        "date": None,
    }


def test_valid_event(validator, valid_event):
    result = validator.validate_event(valid_event)
    assert result["is_valid"] is True
    assert result["errors"] == []
    assert result["quality_score"] == 100


def test_missing_title(validator, valid_event):
    valid_event["title"] = ""
    result = validator.validate_event(valid_event)
    assert result["is_valid"] is False
    assert any("title" in e.lower() for e in result["errors"])


def test_short_title(validator, valid_event):
    valid_event["title"] = "Hi"
    result = validator.validate_event(valid_event)
    assert result["is_valid"] is False


def test_invalid_url_no_scheme(validator, valid_event):
    valid_event["url"] = "example.com/event"
    result = validator.validate_event(valid_event)
    assert result["is_valid"] is False
    assert any("url" in e.lower() for e in result["errors"])


def test_invalid_url_empty(validator, valid_event):
    valid_event["url"] = ""
    result = validator.validate_event(valid_event)
    assert result["is_valid"] is False


def test_null_date_is_valid(validator, valid_event):
    valid_event["date"] = None
    result = validator.validate_event(valid_event)
    assert result["is_valid"] is True


def test_missing_description_lowers_score(validator, valid_event):
    valid_event["description"] = None
    result = validator.validate_event(valid_event)
    assert result["is_valid"] is True
    assert result["quality_score"] < 100


def test_missing_image_lowers_score(validator, valid_event):
    valid_event["image_url"] = None
    result = validator.validate_event(valid_event)
    assert result["quality_score"] < 100


def test_missing_location_lowers_score(validator, valid_event):
    valid_event["location"] = None
    result = validator.validate_event(valid_event)
    assert result["quality_score"] < 100


def test_quality_score_multiple_missing(validator, valid_event):
    valid_event["description"] = None
    valid_event["image_url"] = None
    valid_event["location"] = None
    result = validator.validate_event(valid_event)
    assert result["quality_score"] == 70
