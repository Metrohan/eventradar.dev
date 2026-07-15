import logging
import smtplib
from html import escape
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate, make_msgid, parseaddr
from markdown import markdown

from ..core.config import settings

logger = logging.getLogger(__name__)

SITE_URL = "https://eventradar.dev"


def _is_configured() -> bool:
    return bool(settings.smtp_host and settings.smtp_user and settings.smtp_pass)


def _send(
    to: str,
    subject: str,
    html_body: str,
    *,
    text_body: str = "",
    unsubscribe_url: str | None = None,
) -> bool:
    """SMTP üzerinden e-posta gönderir (düz metin + HTML). Başarılıysa True döner."""
    if not _is_configured():
        logger.info(
            "[DEV] SMTP yapılandırılmamış, e-posta gönderilmedi: %s -> %s", to, subject
        )
        return False

    from_addr = settings.smtp_from
    _, from_email = parseaddr(from_addr)
    domain = from_email.split("@")[-1] if "@" in from_email else "eventradar.dev"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = make_msgid(domain=domain)
    if unsubscribe_url:
        # RFC 2369 — spam filtreleri ve mail sağlayıcıları (Gmail/Outlook) bu
        # başlığı görünce gönderen adına "Abonelikten çık" kısayolu gösterir,
        # bu da bulk mail'de kullanıcıların "spam" tuşlaması yerine düzgün
        # çıkış yapmasını sağlar ve deliverability'yi iyileştirir.
        msg["List-Unsubscribe"] = f"<{unsubscribe_url}>"
    # Düz metin parçası önce eklenmeli: multipart/alternative'de son parça
    # tercih edilen (HTML) olarak render edilir, ama düz metin alternatifinin
    # varlığı da spam filtreleri için önemli bir sinyaldir.
    msg.attach(MIMEText(text_body or _html_to_text(html_body), "plain", "utf-8"))
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as server:
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_pass)
            server.sendmail(from_email, to, msg.as_string())
        return True
    except Exception as exc:
        logger.error("E-posta gönderilemedi (%s): %s", to, exc)
        return False


def _html_to_text(html_body: str) -> str:
    """Kaba bir HTML→düz metin dönüşümü (yalnızca fallback için)."""
    import re

    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", html_body, flags=re.S)
    text = re.sub(r"<(br|/p|/div|/tr|/h[1-6])\s*/?>", "\n", text, flags=re.I)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    return text.strip()


# Marka renkleri (frontend/src/index.css ile aynı palet)
ACCENT = "#38BDF8"
ACCENT_DARK = "#0EA5E9"
INK = "#0B1120"
BODY_TEXT = "#334155"
MUTED_TEXT = "#94A3B8"
CARD_BG = "#FFFFFF"
PAGE_BG = "#F1F5F9"
BORDER = "#E2E8F0"
FONT_STACK = (
    "-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif"
)


def _button(url: str, label: str) -> str:
    return (
        f'<a href="{url}" style="display:inline-block;padding:12px 28px;'
        f"background:{ACCENT};color:{INK};text-decoration:none;border-radius:8px;"
        f'font-weight:700;font-size:15px">{label}</a>'
    )


def _wrapper(inner_html: str, unsubscribe_url: str | None = None) -> str:
    """Tüm e-postalar için ortak, marka uyumlu HTML iskeleti."""
    footer_unsub = (
        f' &middot; <a href="{unsubscribe_url}" style="color:{MUTED_TEXT}">Abonelikten çık</a>'
        if unsubscribe_url
        else ""
    )
    return f"""\
<!DOCTYPE html>
<html lang="tr">
  <body style="margin:0;padding:0;background:{PAGE_BG};font-family:{FONT_STACK}">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:{PAGE_BG};padding:32px 16px">
      <tr>
        <td align="center">
          <table role="presentation" width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%">
            <tr>
              <td align="center" style="padding:0 0 20px">
                <a href="{SITE_URL}" style="text-decoration:none;display:inline-flex;align-items:center;gap:8px">
                  <img src="{SITE_URL}/techeventradar_logo.png" width="28" height="28" alt="" style="vertical-align:middle;border-radius:6px">
                  <span style="font-size:16px;font-weight:700;color:{INK};vertical-align:middle">TechEventRadar</span>
                </a>
              </td>
            </tr>
            <tr>
              <td style="background:{CARD_BG};border:1px solid {BORDER};border-radius:14px;padding:36px;color:{BODY_TEXT};font-size:15px;line-height:1.65">
                {inner_html}
              </td>
            </tr>
            <tr>
              <td align="center" style="padding:22px 12px 0;color:{MUTED_TEXT};font-size:12px;line-height:1.6">
                Türkiye'deki tech etkinliklerini tek yerde topluyoruz.<br>
                <a href="{SITE_URL}" style="color:{MUTED_TEXT}">eventradar.dev</a>{footer_unsub}
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
  </body>
</html>"""


def send_confirmation_email(email: str, confirm_token: str) -> bool:
    confirm_url = f"{SITE_URL}/abone-onay?token={confirm_token}"
    inner = f"""
      <h2 style="margin:0 0 12px;color:{INK};font-size:20px">Aboneliğini onayla</h2>
      <p style="margin:0 0 24px">Haftalık etkinlik özetlerini almak için aboneliğini onaylaman gerekiyor.</p>
      <p style="margin:0 0 24px">{_button(confirm_url, "Aboneliği Onayla")}</p>
      <p style="margin:0;color:{MUTED_TEXT};font-size:13px">Bu isteği sen yapmadıysan bu e-postayı yok sayabilirsin.</p>
    """
    text = (
        "Aboneliğini onayla\n\n"
        "Haftalık etkinlik özetlerini almak için aboneliğini onaylaman gerekiyor.\n\n"
        f"Onayla: {confirm_url}\n\n"
        "Bu isteği sen yapmadıysan bu e-postayı yok sayabilirsin."
    )
    return _send(
        email, "TechEventRadar aboneliğini onayla", _wrapper(inner), text_body=text
    )


def send_weekly_digest_email(
    email: str, events: list[dict], unsubscribe_token: str
) -> bool:
    unsubscribe_url = f"{SITE_URL}/abone-iptal?token={unsubscribe_token}"
    if events:
        items = "".join(
            f'<tr><td style="padding:12px 0;border-bottom:1px solid {BORDER}">'
            f'<a href="{SITE_URL}/etkinlik/{e["id"]}" style="color:{INK};font-weight:600;text-decoration:none;font-size:15px">{e["title"]}</a>'
            f'<div style="color:{MUTED_TEXT};font-size:13px;margin-top:2px">{e.get("source", "")}</div>'
            "</td></tr>"
            for e in events[:15]
        )
        body = f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0">{items}</table>'
    else:
        body = f'<p style="color:{MUTED_TEXT}">Bu hafta yeni etkinlik eklenmedi.</p>'

    inner = f"""
      <h2 style="margin:0 0 4px;color:{INK};font-size:20px">Haftalık Etkinlik Özeti</h2>
      <p style="margin:0 0 20px;color:{MUTED_TEXT};font-size:13px">Bu hafta eklenen etkinlikler</p>
      {body}
      <p style="margin:24px 0 0">{_button(SITE_URL, "Tüm Etkinlikleri Gör")}</p>
    """
    if events:
        text_items = "\n".join(
            f'- {e["title"]} ({e.get("source", "")}): {SITE_URL}/etkinlik/{e["id"]}'
            for e in events[:15]
        )
        text_body = f"Bu hafta eklenen etkinlikler:\n\n{text_items}"
    else:
        text_body = "Bu hafta yeni etkinlik eklenmedi."
    text = (
        f"Haftalık Etkinlik Özeti\n\n{text_body}\n\n"
        f"Tüm etkinlikleri gör: {SITE_URL}\n\n"
        f"Abonelikten çık: {unsubscribe_url}"
    )
    return _send(
        email,
        "TechEventRadar — Haftalık Etkinlik Özeti",
        _wrapper(inner, unsubscribe_url),
        text_body=text,
        unsubscribe_url=unsubscribe_url,
    )


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
    inner = f"""
      <h1 style="margin:0 0 10px;color:{INK};font-size:24px;line-height:1.3">{safe_title}</h1>
      <p style="margin:0 0 20px;color:{MUTED_TEXT};font-size:15px">{safe_summary}</p>
      <hr style="border:none;border-top:1px solid {BORDER};margin:0 0 24px">
      <div style="color:{BODY_TEXT}">{rendered_content}</div>
      <p style="margin:28px 0 0">{_button(post_url, "Yazıyı EventRadar'da Aç")}</p>
    """
    text = (
        f"{title}\n\n{summary}\n\n{content}\n\n"
        f"Yazıyı EventRadar'da aç: {post_url}\n\n"
        f"Abonelikten çık: {unsubscribe_url}"
    )
    return _send(
        email,
        title,
        _wrapper(inner, unsubscribe_url),
        text_body=text,
        unsubscribe_url=unsubscribe_url,
    )
