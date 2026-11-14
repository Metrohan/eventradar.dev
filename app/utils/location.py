"""Pure parsing of the free-text event location into attendance / city / venue.

No imports from the rest of the app on purpose: the Event model uses this, and
``app.services`` imports the models.

Nothing is guessed. A city is assigned only when the text names one of the 81
provinces or a curated district/neighbourhood; anything else stays ``None``.
University and venue names are deliberately not mapped to a city.
"""

import re
import unicodedata
from dataclasses import dataclass

ONLINE = "online"
IN_PERSON = "in_person"
HYBRID = "hybrid"

# fmt: off
PROVINCES = (
    "Adana", "Adıyaman", "Afyonkarahisar", "Ağrı", "Aksaray", "Amasya", "Ankara",
    "Antalya", "Ardahan", "Artvin", "Aydın", "Balıkesir", "Bartın", "Batman",
    "Bayburt", "Bilecik", "Bingöl", "Bitlis", "Bolu", "Burdur", "Bursa",
    "Çanakkale", "Çankırı", "Çorum", "Denizli", "Diyarbakır", "Düzce", "Edirne",
    "Elazığ", "Erzincan", "Erzurum", "Eskişehir", "Gaziantep", "Giresun",
    "Gümüşhane", "Hakkâri", "Hatay", "Iğdır", "Isparta", "İstanbul", "İzmir",
    "Kahramanmaraş", "Karabük", "Karaman", "Kars", "Kastamonu", "Kayseri",
    "Kırıkkale", "Kırklareli", "Kırşehir", "Kilis", "Kocaeli", "Konya", "Kütahya",
    "Malatya", "Manisa", "Mardin", "Mersin", "Muğla", "Muş", "Nevşehir", "Niğde",
    "Ordu", "Osmaniye", "Rize", "Sakarya", "Samsun", "Siirt", "Sinop", "Sivas",
    "Şanlıurfa", "Şırnak", "Tekirdağ", "Tokat", "Trabzon", "Tunceli", "Uşak",
    "Van", "Yalova", "Yozgat", "Zonguldak",
)
# fmt: on

# Ordinary words as well as provinces: only an exact whole-value match counts.
_WHOLE_VALUE_ONLY = {"van", "ordu"}

# Curated, not exhaustive. Names that are also common words or exist in more
# than one province (Adalar, Selçuk, Tire, Kiraz, Menderes, Gölbaşı, Konak...)
# are left out on purpose.
# fmt: off
_DISTRICTS = {
    "İstanbul": (
        "Arnavutköy", "Ataşehir", "Avcılar", "Bağcılar", "Bahçelievler",
        "Bakırköy", "Başakşehir", "Bayrampaşa", "Beşiktaş", "Beykoz",
        "Beylikdüzü", "Beyoğlu", "Büyükçekmece", "Çatalca", "Çekmeköy",
        "Esenler", "Esenyurt", "Eyüpsultan", "Fatih", "Gaziosmanpaşa",
        "Güngören", "Kadıköy", "Kağıthane", "Kartal", "Küçükçekmece", "Maltepe",
        "Pendik", "Sancaktepe", "Sarıyer", "Silivri", "Sultanbeyli",
        "Sultangazi", "Şile", "Şişli", "Tuzla", "Ümraniye", "Üsküdar",
        "Zeytinburnu",
        # Neighbourhoods seen in scraped data or unambiguously in Istanbul.
        "Şişhane", "Kayışdağı", "Ayazağa", "Maslak", "Taksim", "Karaköy",
    ),
    "Ankara": (
        "Altındağ", "Çankaya", "Etimesgut", "Keçiören", "Mamak", "Polatlı",
        "Pursaklar", "Sincan", "Yenimahalle",
    ),
    "İzmir": (
        "Balçova", "Bayraklı", "Bornova", "Buca", "Çeşme", "Çiğli", "Gaziemir",
        "Güzelbahçe", "Karabağlar", "Karşıyaka", "Menemen", "Narlıdere", "Urla",
    ),
}
# fmt: on


def search_key(value: str) -> str:
    """Lower-case, accent-free, dotless-i-free key for matching."""
    normalized = unicodedata.normalize("NFKD", value.casefold().replace("ı", "i"))
    ascii_value = "".join(c for c in normalized if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", ascii_value).strip()


_PROVINCE_KEYS = {search_key(name): name for name in PROVINCES}
_DISTRICT_KEYS = {
    search_key(district): city
    for city, districts in _DISTRICTS.items()
    for district in districts
}
_ONLINE_RE = re.compile(r"\b(online|cevrim ?ici|remote|uzaktan|zoom)\b")
_HYBRID_RE = re.compile(r"\b(hibrit|hybrid)\b")
_FILLER = {"ve", "ile", "and", "etkinlik", "etkinligi", "canli"}


@dataclass(frozen=True)
class LocationInfo:
    attendance: str | None = None
    city: str | None = None
    venue: str | None = None


def _city_of(key: str) -> str | None:
    if key in _PROVINCE_KEYS and key in _WHOLE_VALUE_ONLY:
        return _PROVINCE_KEYS[key]
    cities = set()
    for token in re.findall(r"[a-z0-9]+", key):
        if token in _PROVINCE_KEYS and token not in _WHOLE_VALUE_ONLY:
            cities.add(_PROVINCE_KEYS[token])
        elif token in _DISTRICT_KEYS:
            cities.add(_DISTRICT_KEYS[token])
    # Two different cities in one value is ambiguous: say nothing.
    return cities.pop() if len(cities) == 1 else None


def parse_location(raw: str | None) -> LocationInfo:
    cleaned = re.sub(r"\s+", " ", raw or "").strip()
    if not cleaned or cleaned == "-":
        return LocationInfo()
    key = search_key(cleaned)
    remainder = _HYBRID_RE.sub(" ", _ONLINE_RE.sub(" ", key))
    has_physical = any(
        token not in _FILLER for token in re.findall(r"[a-z0-9]+", remainder)
    )
    is_online = bool(_ONLINE_RE.search(key))
    if _HYBRID_RE.search(key) or (is_online and has_physical):
        attendance = HYBRID
    elif is_online:
        attendance = ONLINE
    else:
        attendance = IN_PERSON
    return LocationInfo(
        attendance=attendance,
        city=_city_of(key),
        venue=None if attendance == ONLINE else cleaned,
    )
