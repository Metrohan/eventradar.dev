"""How relevant an event is to a tech audience: a tier and a reason.

Since 2026-11-15 this no longer hides anything. Every scraped event is shown;
the API exposes the tier as ``topic`` and visitors can narrow the list with the
"tech related" filter. ``EventIngestion`` still accepts a ``topic_filter`` and
``scripts/review_topic_scope.py`` can still plan hides, but production does
not enable either.

Reversible topic scope for scraped events (how the tier is decided).

The question is not "is this purely technical?" but "is it relevant to a tech
audience?". A career summit for engineers or a talk by a CTO belongs on the
site even though it teaches no code. Four rules, in this order, each with a
reason that the review script can show:

1. A technical term in the title (software, data/AI, security, electronics...).
2. A tech-career/role term in the title (engineering, CTO, startup, hackathon,
   product management, career summit...). Title only: a description that merely
   mentions an engineer does not make a food-science day technical. Every
   career summit is kept: the site does not decide which ones are "tech enough";
   a visitor can narrow the list with the search box.
3. An explicit non-tech topic in the title (payroll, retail, a brand's youth
   academy...) hides the event, even when the description mentions AI.
4. A technical term in the description, or an event from a source that only
   lists technology events (see ``_TECH_SOURCES``).

Everything else is hidden. A bare format word (bootcamp, summit, seminar) is
not evidence on its own; "hackathon" and "datathon" are,
because they mean building software, "ideathon" is not.
"""

import re
import unicodedata
from dataclasses import dataclass


def _normalise(value: str) -> str:
    value = value.lower().replace("c++", "cplusplus").replace("c#", "csharp")
    # A Turkish suffix after an apostrophe ("CTO’nun", "Python'da") must not
    # glue to the word, or the term loses its word boundary.
    value = re.sub("[’'`´]", " ", value)
    value = value.translate(str.maketrans("ıİşŞğĞüÜöÖçÇ", "iIsSgGuUoOcC"))
    return (
        unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().lower()
    )


_TECHNICAL = re.compile(
    r"\b(?:yazilim\w*|kodlama|kodluyoruz|python|javascript|typescript|java|kotlin|swift|"
    r"rust|golang|cplusplus|csharp|veri|data|yapay zeka|artificial intelligence|ai|ml|claude|chatgpt|machine learning|"
    r"deep learning|generative|agentic|siber|cyber\w*|bilgisayar|computer science|"
    r"elektronik|electronics|gomulu|embedded|robotik|robotics|iot|devops|cloud|bulut|"
    r"teknoloji|technology|no[ -]?code|low[ -]?code|sql|linux|network engineering|network security|ag teknolojileri|sebeke|"
    r"blockchain|web3|software|programlama|programming)\b"
)
# Relevant to people who work in tech without being technical content itself.
_ADJACENT = re.compile(
    r"\b(?:cto|cio|chief technology|engineering|muhendis\w*|tech lead|engineering manager|"
    r"startup|product management|urun yonetimi|product owner|agile|scrum|ux|"
    r"hackathon|datathon|open source|acik kaynak|developer|gelistirici|programci|"
    r"career summit|kariyer zirvesi)\b"
)
# Explicit non-tech topics. They override weak evidence (description, source),
# not a technical term in the title.
_GENERAL_TITLE = re.compile(
    r"\b(?:talent summit|business strategy|future of hr|retail challenge|"
    r"youth academy|mentor|case maratonu|fellowship|girisimcilik okulu|cool chain|"
    r"payroll|youtalkz|hikaye hasadi)\b"
)
# Sources that only list technology events (names as stored in Event.source).
# Tech Istanbul is deliberately not here: it also runs entrepreneurship and
# business seminars (sales, branding, legal set-up) that are not tech content.
_TECH_SOURCES = frozenset(
    {"kodluyoruz", "pupilica", "coderspace", "techcareer.net", "patika.dev"}
)


@dataclass(frozen=True)
class TopicDecision:
    allowed: bool
    tier: str  # technical | adjacent | source | general
    reason: str


def classify_event(
    title: str | None, description: str | None = None, source: str | None = None
) -> TopicDecision:
    title_text = _normalise(title or "")
    description_text = _normalise(description or "")
    if match := _TECHNICAL.search(title_text):
        return TopicDecision(True, "technical", f"title: {match.group(0)}")
    if match := _ADJACENT.search(title_text):
        return TopicDecision(True, "adjacent", f"title: {match.group(0)}")
    if match := _GENERAL_TITLE.search(title_text):
        return TopicDecision(False, "general", f"not tech: {match.group(0)}")
    if match := _TECHNICAL.search(description_text):
        return TopicDecision(True, "technical", f"description: {match.group(0)}")
    if _normalise(source or "") in _TECH_SOURCES:
        return TopicDecision(True, "source", f"tech source: {source}")
    return TopicDecision(False, "general", "no technical evidence")


def is_technical_event(
    title: str | None, description: str | None = None, source: str | None = None
) -> bool:
    return classify_event(title, description, source).allowed


def announceable(events):
    """Keep the events that are worth announcing (Telegram, push).

    Every event is listed on the site; the announcements are the channel for
    people who asked to hear about technology events, so the ones with no
    technical relevance are left out. Items are mappings with ``title``,
    ``description`` and ``source``.
    """
    return [
        event
        for event in events
        if is_technical_event(
            event.get("title"), event.get("description"), event.get("source")
        )
    ]
