import re
from typing import Any


_URL_RE = re.compile(r"^https?://\S+")


class EventValidator:
    def validate_title(self, title: Any) -> list[str]:
        errors = []
        if not title or not str(title).strip():
            errors.append("title: boş olamaz")
        elif len(str(title).strip()) < 5:
            errors.append("title: en az 5 karakter olmalı")
        return errors

    def validate_url(self, url: Any) -> list[str]:
        errors = []
        if not url or not str(url).strip():
            errors.append("url: boş olamaz")
        elif not _URL_RE.match(str(url).strip()):
            errors.append("url: geçerli bir HTTP(S) URL olmalı")
        return errors

    def validate_event(self, event: dict) -> dict:
        errors = []
        errors.extend(self.validate_title(event.get("title")))
        errors.extend(self.validate_url(event.get("url")))

        score = 100
        if not event.get("description"):
            score -= 10
        if not event.get("image_url"):
            score -= 10
        if not event.get("location"):
            score -= 10

        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "quality_score": max(0, score),
        }
