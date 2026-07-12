from dataclasses import dataclass
from importlib import import_module
from typing import Callable, Literal

RunnerMode = Literal["static", "browser"]
ScraperRunner = Callable[[], list[dict]]


def _lazy_runner(module_path: str, function_name: str) -> ScraperRunner:
    def run() -> list[dict]:
        module = import_module(module_path)
        return getattr(module, function_name)()

    return run


@dataclass(frozen=True)
class SourceDefinition:
    key: str
    name: str
    website: str
    mode: RunnerMode
    enabled: bool
    runner: ScraperRunner
    aliases: tuple[str, ...] = ()

    @property
    def identifiers(self) -> tuple[str, ...]:
        return (self.name, *self.aliases)

    def public_dict(self) -> dict:
        return {
            "key": self.key,
            "name": self.name,
            "website": self.website,
            "mode": self.mode,
            "enabled": self.enabled,
        }


SOURCE_CATALOG: tuple[SourceDefinition, ...] = (
    SourceDefinition(
        "kodluyoruz",
        "Kodluyoruz",
        "https://www.kodluyoruz.org",
        "static",
        True,
        _lazy_runner("app.scrapers.kodluyoruz_scraper", "scrape_kodluyoruz_events"),
    ),
    SourceDefinition(
        "anbean",
        "Anbean",
        "https://anbeankampus.co",
        "static",
        True,
        _lazy_runner("app.scrapers.anbean_scraper", "scrape_anbean_events"),
    ),
    SourceDefinition(
        "akbank-genclik-akademisi",
        "Akbank Gençlik Akademisi",
        "https://www.akbanklab.com/tr/genc-akbanklilar",
        "static",
        True,
        _lazy_runner("app.scrapers.akbank_scraper", "scrape_akbank_events"),
        ("Akbank",),
    ),
    SourceDefinition(
        "pupilica",
        "Pupilica",
        "https://pupilica.com",
        "static",
        True,
        _lazy_runner("app.scrapers.pupilica_scraper", "scrape_pupilica_events"),
    ),
    SourceDefinition(
        "tech-istanbul",
        "Tech Istanbul",
        "https://tech.istanbul/etkinlikler",
        "static",
        True,
        _lazy_runner("app.scrapers.techistanbul_scraper", "scrape_techistanbul_events"),
    ),
    SourceDefinition(
        "patika",
        "Patika.dev",
        "https://www.patika.dev/bootcamp",
        "static",
        True,
        _lazy_runner("app.scrapers.patika_scraper", "scrape_patika_events"),
    ),
    SourceDefinition(
        "komunite",
        "Komünite",
        "https://komunite.com.tr/etkinlikler",
        "static",
        True,
        _lazy_runner("app.scrapers.komunite_scraper", "scrape_komunite_events"),
    ),
    SourceDefinition(
        "techcareer",
        "TechCareer.net",
        "https://www.techcareer.net/events",
        "browser",
        True,
        _lazy_runner("app.scrapers.techcareer_scraper", "scrape_techcareer_events"),
    ),
    SourceDefinition(
        "youthall",
        "Youthall",
        "https://www.youthall.com/tr/events",
        "browser",
        True,
        _lazy_runner("app.scrapers.youthall_scraper", "scrape_youthall_events"),
    ),
    SourceDefinition(
        "coderspace",
        "Coderspace",
        "https://coderspace.io/etkinlikler",
        "browser",
        True,
        _lazy_runner("app.scrapers.cs_scraper", "scrape_coderspace_events"),
    ),
)


def get_enabled_sources() -> tuple[SourceDefinition, ...]:
    return tuple(source for source in SOURCE_CATALOG if source.enabled)


def get_source(identifier: str) -> SourceDefinition | None:
    normalized = identifier.strip().casefold()
    return next(
        (
            source
            for source in SOURCE_CATALOG
            if normalized
            in {
                source.key.casefold(),
                *(value.casefold() for value in source.identifiers),
            }
        ),
        None,
    )
