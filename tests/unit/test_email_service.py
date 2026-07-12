from unittest.mock import patch

from app.services import email_service


def test_weekly_blog_email_renders_content_and_unsubscribe_link():
    with patch.object(email_service, "_send", return_value=True) as send:
        result = email_service.send_weekly_blog_email(
            "reader@example.com",
            "Bu Haftanın Etkinlikleri",
            "Haftalık özet",
            "## AI Hackathon\n\n[Etkinliği incele](https://example.com/event)",
            "haftalik-etkinlikler-2026-07-13",
            "unsubscribe-token",
        )

    assert result is True
    html = send.call_args.args[2]
    assert "<h2>AI Hackathon</h2>" in html
    assert "https://eventradar.dev/blog/haftalik-etkinlikler-2026-07-13" in html
    assert "abone-iptal?token=unsubscribe-token" in html


def test_weekly_blog_email_escapes_raw_html():
    with patch.object(email_service, "_send", return_value=True) as send:
        email_service.send_weekly_blog_email(
            "reader@example.com",
            "<script>title</script>",
            "<img src=x>",
            "<script>alert(1)</script>",
            "weekly",
            "token",
        )

    html = send.call_args.args[2]
    assert "<script>" not in html
    assert "<img src=x>" not in html
