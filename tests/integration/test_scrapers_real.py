import os

os.environ.setdefault("ALLOW_INSECURE_DEFAULTS", "true")
os.environ.setdefault("SECRET_KEY", "test-secret-key-that-is-at-least-32-chars")
os.environ.setdefault("ADMIN_USERNAME", "testadmin")
os.environ.setdefault("ADMIN_PASSWORD", "testpassword")

import pytest


@pytest.mark.integration
def test_youthall_real():
    from app.scrapers.youthall_scraper import scrape_youthall_events
    events = scrape_youthall_events()
    assert isinstance(events, list)


@pytest.mark.integration
def test_techcareer_real():
    from app.scrapers.techcareer_scraper import scrape_techcareer_events
    events = scrape_techcareer_events()
    assert isinstance(events, list)


@pytest.mark.integration
def test_kodluyoruz_real():
    from app.scrapers.kodluyoruz_scraper import scrape_kodluyoruz_events
    events = scrape_kodluyoruz_events()
    assert isinstance(events, list)


@pytest.mark.integration
def test_anbean_real():
    from app.scrapers.anbean_scraper import scrape_anbean_events
    events = scrape_anbean_events()
    assert isinstance(events, list)
