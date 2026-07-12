from importlib import import_module
from typing import Callable

_RUNNERS = {
    "scrape_techcareer_events": ("techcareer_scraper", "scrape_techcareer_events"),
    "scrape_coderspace_events": ("cs_scraper", "scrape_coderspace_events"),
    "scrape_anbean_events": ("anbean_scraper", "scrape_anbean_events"),
    "scrape_kodluyoruz_events": ("kodluyoruz_scraper", "scrape_kodluyoruz_events"),
    "scrape_youthall_events": ("youthall_scraper", "scrape_youthall_events"),
    "scrape_techistanbul_events": ("techistanbul_scraper", "scrape_techistanbul_events"),
    "scrape_patika_events": ("patika_scraper", "scrape_patika_events"),
    "scrape_komunite_events": ("komunite_scraper", "scrape_komunite_events"),
}

__all__ = list(_RUNNERS)


def __getattr__(name: str) -> Callable[[], list[dict]]:
    try:
        module_name, function_name = _RUNNERS[name]
    except KeyError as exc:
        raise AttributeError(name) from exc
    return getattr(import_module(f"{__name__}.{module_name}"), function_name)
