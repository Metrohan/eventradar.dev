import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

os.environ.setdefault("ALLOW_INSECURE_DEFAULTS", "true")
os.environ.setdefault("SECRET_KEY", "test-secret-key-that-is-at-least-32-chars")
os.environ.setdefault("ADMIN_USERNAME", "testadmin")
os.environ.setdefault("ADMIN_PASSWORD", "testpassword")

from app.core.database import Base


@pytest.fixture(scope="function")
def test_db():
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def valid_event():
    return {
        "title": "Python Bootcamp Istanbul",
        "date": "2027-05-15",
        "location": "Istanbul",
        "url": "https://example.com/events/python-bootcamp",
        "source": "test",
        "description": "A great Python bootcamp",
        "image_url": "https://example.com/image.jpg",
    }


@pytest.fixture
def invalid_event():
    return {
        "title": "",
        "date": "not-a-date",
        "location": "",
        "url": "not-a-url",
        "source": "test",
    }
