import os

os.environ.setdefault("ALLOW_INSECURE_DEFAULTS", "true")
os.environ.setdefault("SECRET_KEY", "test-secret-key-that-is-at-least-32-chars")
os.environ.setdefault("ADMIN_USERNAME", "testadmin")
os.environ.setdefault("ADMIN_PASSWORD", "testpassword")


# ── /robots.txt ───────────────────────────────────────────────────────────────


def test_robots_txt_is_served_as_plain_text(client):
    resp = client.get("/robots.txt")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/plain")


def test_robots_txt_allows_api_but_blocks_admin(client):
    body = client.get("/robots.txt").text
    # Regression: production robots.txt used to blanket-block /api/, which also
    # hid /api/events/rss and the dynamic sitemap from Google.
    assert "Disallow: /api/\n" not in body
    assert "Disallow: /admin/" in body
    assert "Disallow: /api/admin/" in body


def test_robots_txt_advertises_sitemap(client):
    body = client.get("/robots.txt").text
    assert "Sitemap: https://eventradar.dev/sitemap.xml" in body


def test_sitemap_xml_still_reachable(client):
    resp = client.get("/sitemap.xml")
    assert resp.status_code == 200
    assert "<urlset" in resp.text
