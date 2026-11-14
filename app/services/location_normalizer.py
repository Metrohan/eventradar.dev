import re

from ..utils.location import search_key as _search_key

ONLINE_VALUES = {
    "online",
    "online etkinlik",
    "çevrimiçi",
    "cevrimici",
    "remote",
    "uzaktan",
}

CITY_NAMES = {
    "istanbul": "İstanbul",
    "ankara": "Ankara",
    "izmir": "İzmir",
    "adana": "Adana",
    "antalya": "Antalya",
    "bursa": "Bursa",
    "eskisehir": "Eskişehir",
    "elazig": "Elazığ",
    "kocaeli": "Kocaeli",
}


def normalize_location(value: str | None) -> str | None:
    if not value or not value.strip() or value.strip() == "-":
        return None

    cleaned = re.sub(r"\s+", " ", value).strip()
    key = _search_key(cleaned)
    if key in {_search_key(item) for item in ONLINE_VALUES}:
        return "Online"
    if key in CITY_NAMES:
        return CITY_NAMES[key]
    return cleaned
