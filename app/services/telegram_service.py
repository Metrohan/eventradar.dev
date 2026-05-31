# app/services/telegram_service.py
import logging
import os
import time

import requests

logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHANNEL_ID: str = os.getenv("TELEGRAM_CHANNEL_ID", "")

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
    return bool(TELEGRAM_BOT_TOKEN and TELEGRAM_CHANNEL_ID)


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
    lines.extend(["", f'🔗 <a href="{url}">Detaylar →</a>'])

    return "\n".join(lines)


def _send_message(text: str) -> bool:
    """Kanala metin mesajı gönderir. Başarılıysa True döner."""
    if not _is_configured():
        return False
    api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        resp = requests.post(
            api_url,
            json={
                "chat_id": TELEGRAM_CHANNEL_ID,
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
    if not _is_configured():
        return False
    api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    try:
        resp = requests.post(
            api_url,
            json={
                "chat_id": TELEGRAM_CHANNEL_ID,
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
        title = event.get("title", "")
        url = event.get("url", "")
        lines.append(f'• <a href="{url}">{title}</a>')

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
