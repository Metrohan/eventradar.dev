import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

os.environ.setdefault("ALLOW_INSECURE_DEFAULTS", "true")
os.environ.setdefault("SECRET_KEY", "test-secret-key-that-is-at-least-32-chars")
os.environ.setdefault("ADMIN_USERNAME", "testadmin")
os.environ.setdefault("ADMIN_PASSWORD", "testpassword")

from app.core.database import Base

# Import all models so Base.metadata is populated before create_all
import app.models.event  # noqa: F401
import app.models.announcement  # noqa: F401
import app.models.suggestion  # noqa: F401
import app.models.event_request  # noqa: F401
import app.models.scraper_log  # noqa: F401
import app.models.subscriber  # noqa: F401
import app.models.traffic_log  # noqa: F401
import app.models.pending_event  # noqa: F401
import app.models.similar_event_pair  # noqa: F401
import app.models.tag  # noqa: F401
import app.models.blog_post  # noqa: F401


@pytest.fixture(scope="function")
def test_db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


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


from fastapi.testclient import TestClient


@pytest.fixture
def client(test_db):
    from app.main import app
    from app.core.database import get_db

    app.dependency_overrides[get_db] = lambda: test_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client):
    import os

    resp = client.post(
        "/api/admin/login",
        json={
            "username": os.environ["ADMIN_USERNAME"],
            "password": os.environ["ADMIN_PASSWORD"],
        },
    )
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
