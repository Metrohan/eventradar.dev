from sqlalchemy.orm import Session
from ..models.tag import Tag

KEYWORD_MAP = {
    "hackathon": ["hackathon", "hack", "datathon", "ideathon"],
    "seminer":   ["seminer", "webinar", "sunum", "söyleşi", "konuşma"],
    "atolye":    ["atölye", "workshop", "lab", "pratik", "uygulama"],
    "konferans": ["konferans", "summit", "zirve", "conference"],
    "bootcamp":  ["bootcamp", "boot camp", "yoğun eğitim", "kamp"],
}

_SEED_DATA = [
    {"name": "hackathon", "label": "Hackathon",         "color": "blue"},
    {"name": "seminer",   "label": "Seminer / Webinar",  "color": "purple"},
    {"name": "atolye",    "label": "Atölye",             "color": "green"},
    {"name": "konferans", "label": "Konferans",           "color": "orange"},
    {"name": "bootcamp",  "label": "Bootcamp",            "color": "pink"},
    {"name": "diger",     "label": "Diğer",               "color": "gray"},
]


def classify_event(title: str, description: str | None) -> list[str]:
    text = (title + " " + (description or "")).lower()
    matched = [
        name
        for name, keywords in KEYWORD_MAP.items()
        if any(kw in text for kw in keywords)
    ]
    return matched if matched else ["diger"]


def seed_tags(db: Session) -> None:
    existing = {t.name for t in db.query(Tag).all()}
    for data in _SEED_DATA:
        if data["name"] not in existing:
            db.add(Tag(**data))
    db.commit()
