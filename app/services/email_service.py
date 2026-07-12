import logging
import smtplib
from html import escape
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from markdown import markdown

from ..core.config import settings

logger = logging.getLogger(__name__)

SITE_URL = "https://eventradar.dev"


def _is_configured() -> bool:
    return bool(settings.smtp_host and settings.smtp_user and settings.smtp_pass)


def _send(to: str, subject: str, html_body: str) -> bool:
    """SMTP üzerinden HTML e-posta gönderir. Başarılıysa True döner."""
    if not _is_configured():
        logger.info(
            "[DEV] SMTP yapılandırılmamış, e-posta gönderilmedi: %s -> %s", to, subject
        )
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.smtp_from
    msg["To"] = to
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as server:
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_pass)
            server.sendmail(settings.smtp_from, to, msg.as_string())
        return True
    except Exception as exc:
        logger.error("E-posta gönderilemedi (%s): %s", to, exc)
        return False


def send_confirmation_email(email: str, confirm_token: str) -> bool:
    confirm_url = f"{SITE_URL}/abone-onay?token={confirm_token}"
    html = f"""
    <div style="font-family:sans-serif;max-width:480px;margin:0 auto">
      <h2>TechEventRadar aboneliğini onayla</h2>
      <p>Haftalık etkinlik özetlerini almak için aboneliğini onaylaman gerekiyor.</p>
      <p><a href="{confirm_url}" style="display:inline-block;padding:10px 20px;background:#38BDF8;color:#0B1120;text-decoration:none;border-radius:8px;font-weight:600">Aboneliği Onayla</a></p>
      <p style="color:#666;font-size:0.85rem">Bu isteği sen yapmadıysan bu e-postayı yok sayabilirsin.</p>
    </div>
    """
    return _send(email, "TechEventRadar aboneliğini onayla", html)


def send_weekly_digest_email(
    email: str, events: list[dict], unsubscribe_token: str
) -> bool:
    unsubscribe_url = f"{SITE_URL}/abone-iptal?token={unsubscribe_token}"
    if events:
        items = "".join(
            f'<li style="margin-bottom:8px"><a href="{SITE_URL}/etkinlik/{e["id"]}">{e["title"]}</a>'
            f' <span style="color:#888">({e.get("source", "")})</span></li>'
            for e in events[:15]
        )
        body = f"<p>Bu hafta eklenen etkinlikler:</p><ul>{items}</ul>"
    else:
        body = "<p>Bu hafta yeni etkinlik eklenmedi.</p>"

    html = f"""
    <div style="font-family:sans-serif;max-width:480px;margin:0 auto">
      <h2>Haftalık Etkinlik Özeti</h2>
      {body}
      <p><a href="{SITE_URL}">Tüm etkinlikleri gör →</a></p>
      <hr style="border:none;border-top:1px solid #eee;margin:24px 0">
      <p style="color:#999;font-size:0.75rem"><a href="{unsubscribe_url}" style="color:#999">Abonelikten çık</a></p>
    </div>
    """
    return _send(email, "TechEventRadar — Haftalık Etkinlik Özeti", html)


def send_weekly_blog_email(
    email: str,
    title: str,
    summary: str,
    content: str,
    slug: str,
    unsubscribe_token: str,
) -> bool:
    """Send the published weekly blog post as an email newsletter."""
    post_url = f"{SITE_URL}/blog/{slug}"
    unsubscribe_url = f"{SITE_URL}/abone-iptal?token={unsubscribe_token}"
    rendered_content = markdown(escape(content))
    safe_title = escape(title)
    safe_summary = escape(summary)
    html = f"""
    <div style="font-family:sans-serif;max-width:640px;margin:0 auto;line-height:1.6">
      <h1>{safe_title}</h1>
      <p style="color:#555">{safe_summary}</p>
      <hr style="border:none;border-top:1px solid #eee;margin:24px 0">
      {rendered_content}
      <p style="margin-top:28px"><a href="{post_url}">Yazıyı EventRadar'da aç →</a></p>
      <hr style="border:none;border-top:1px solid #eee;margin:24px 0">
      <p style="color:#999;font-size:0.75rem"><a href="{unsubscribe_url}" style="color:#999">Abonelikten çık</a></p>
    </div>
    """
    return _send(email, title, html)
