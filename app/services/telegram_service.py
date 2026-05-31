# app/services/telegram_service.py
import html as html_lib
import logging
import os
import time
from urllib.parse import urlparse

import requests

logger = logging.getLogger(__name__)

_TYPE_EMOJIS = {
    "hackathon": "🏆",
    "bootcamp": "🎓",
    "staj": "💼",
    "seminer": "📚",
    "konferans": "🎤",
    "atolye": "🔧",
    "diğer": "📌",
}


def _is_configured() -> bool:
    """Bot token ve kanal ID'si tanımlanmışsa True döner."""
    return bool(os.getenv("TELEGRAM_BOT_TOKEN") and os.getenv("TELEGRAM_CHANNEL_ID"))


def _detect_type(title: str) -> str:
    """Başlıktan etkinlik türünü tahmin eder."""
    t = title.lower()
    if any(k in t for k in ("hackathon", "datathon", "ideathon")):
        return "hackathon"
    if "bootcamp" in t:
        return "bootcamp"
    if any(k in t for k in ("staj", "internship")):
        return "staj"
    if any(k in t for k in ("webinar", "seminer", "seminar", "söyleşi")):
        return "seminer"
    if any(k in t for k in ("konferans", "summit")):
        return "konferans"
    if any(k in t for k in ("atölye", "workshop")):
        return "atolye"
    return "diğer"


def _format_event_message(event: dict) -> str:
    """Tek etkinlik için zengin formatlı HTML mesajı oluşturur."""
    title = event.get("title", "")
    url = event.get("url", "")
    source = event.get("source", "")
    date_str = event.get("date", "")
    description = event.get("description", "")

    if description and len(description) > 200:
        description = description[:197] + "..."

    # Escape tüm kullanıcı verilerini HTML injection'a karşı
    title = html_lib.escape(title)
    source = html_lib.escape(source)
    date_str = html_lib.escape(date_str)
    description = html_lib.escape(description)
    safe_url = url if urlparse(url).scheme in ("http", "https") else ""

    event_type = _detect_type(title)
    type_emoji = _TYPE_EMOJIS.get(event_type, "📌")

    lines = [
        "🔔 <b>Yeni Etkinlik</b>",
        "",
        f"📌 <b>{title}</b>",
        f"{type_emoji} {event_type.title()} · {source}",
    ]
    if date_str:
        lines.append(f"📅 {date_str}")
    if description:
        lines.append(f"📝 {description}")
    if safe_url:
        lines.extend(["", f'🔗 <a href="{html_lib.escape(safe_url, quote=True)}">Detaylar →</a>'])
    else:
        lines.extend(["", "🔗 (link mevcut değil)"])

    return "\n".join(lines)


def _send_message(text: str) -> bool:
    """Kanala metin mesajı gönderir. Başarılıysa True döner."""
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    channel = os.getenv("TELEGRAM_CHANNEL_ID", "")
    if not (token and channel):
        return False
    api_url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        resp = requests.post(
            api_url,
            json={
                "chat_id": channel,
                "text": text,
                "parse_mode": "HTML",
                "disable_web_page_preview": False,
            },
            timeout=10,
        )
        resp.raise_for_status()
        return True
    except Exception as exc:
        logger.error(f"Telegram sendMessage hatası: {exc}")
        return False


def _send_photo(image_url: str, caption: str) -> bool:
    """Kanala görsel + açıklama gönderir. Başarısız olursa False döner."""
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    channel = os.getenv("TELEGRAM_CHANNEL_ID", "")
    if not (token and channel):
        return False
    api_url = f"https://api.telegram.org/bot{token}/sendPhoto"
    try:
        resp = requests.post(
            api_url,
            json={
                "chat_id": channel,
                "photo": image_url,
                "caption": caption,
                "parse_mode": "HTML",
            },
            timeout=10,
        )
        resp.raise_for_status()
        return True
    except Exception as exc:
        logger.warning(f"Telegram sendPhoto başarısız, metin mesajına geçiliyor: {exc}")
        return False


def notify_new_events(events: list[dict]) -> None:
    """
    Yeni etkinlikler için anlık bildirim gönderir.
    Görsel varsa sendPhoto, yoksa sendMessage kullanır.
    Birden fazla etkinlikte mesajlar arası 0.5s beklenir.
    """
    if not _is_configured() or not events:
        return

    for i, event in enumerate(events):
        text = _format_event_message(event)
        image_url = event.get("image_url", "")

        if image_url:
            success = _send_photo(image_url, text)
            if not success:
                _send_message(text)
        else:
            _send_message(text)

        if i < len(events) - 1:
            time.sleep(0.5)


def send_daily_digest(events: list[dict], date_label: str) -> None:
    """
    Günlük özet gönderir. events boşsa hiçbir şey göndermez.
    date_label: "1 Haziran 2026" formatında string.
    """
    if not _is_configured() or not events:
        return

    lines = [f"📊 <b>Günlük Özet · {date_label}</b>", ""]
    lines.append(f"Bugün <b>{len(events)}</b> yeni etkinlik eklendi:")
    lines.append("")

    for event in events[:10]:
        title = html_lib.escape(event.get("title", ""))
        raw_url = event.get("url", "")
        safe_url = raw_url if urlparse(raw_url).scheme in ("http", "https") else ""
        if safe_url:
            lines.append(f'• <a href="{html_lib.escape(safe_url, quote=True)}">{title}</a>')
        else:
            lines.append(f"• {title}")

    if len(events) > 10:
        lines.append(f"  … ve {len(events) - 10} etkinlik daha")

    lines.extend(["", '👉 <a href="https://eventradar.dev">eventradar.dev</a>'])
    _send_message("\n".join(lines))


def send_weekly_digest(events: list[dict], week_label: str) -> None:
    """
    Haftalık özet gönderir. events boş olsa bile gönderir.
    week_label: "26 Mayıs – 1 Haziran" formatında string.
    """
    if not _is_configured():
        return

    if not events:
        _send_message(
            f"📅 <b>Haftalık Özet · {week_label}</b>\n\n"
            "Bu hafta yeni etkinlik eklenmedi.\n\n"
            '👉 <a href="https://eventradar.dev">eventradar.dev</a>'
        )
        return

    from collections import Counter
    type_counts: Counter = Counter(_detect_type(e.get("title", "")) for e in events)

    lines = [f"📅 <b>Haftalık Özet · {week_label}</b>", ""]
    lines.append(f"Bu hafta <b>{len(events)}</b> etkinlik eklendi:")

    type_parts = []
    for etype, count in type_counts.most_common(4):
        emoji = _TYPE_EMOJIS.get(etype, "📌")
        type_parts.append(f"{emoji} {count} {etype.title()}")
    if type_parts:
        lines.append("   ".join(type_parts))

    lines.extend(["", '👉 <a href="https://eventradar.dev">eventradar.dev</a>'])
    _send_message("\n".join(lines))
