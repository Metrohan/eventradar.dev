import pytest

from app.models.event import Event
from app.utils.location import (
    HYBRID,
    IN_PERSON,
    ONLINE,
    PROVINCES,
    LocationInfo,
    parse_location,
)

KOMUNITE = (
    "Komünite Space, Ayazağa Mah. Azerbaycan Cd. No:3A Radisson Collection "
    "Hotel, Dış Dükkan, Sarıyer / İstanbul"
)


@pytest.mark.parametrize(
    ("raw", "attendance", "city", "has_venue"),
    [
        # The forms seen in the live data on 2026-11-14.
        ("Online", ONLINE, None, False),
        ("Online (Zoom)", ONLINE, None, False),
        ("Hibrit ( Istanbul & Zoom )", HYBRID, "İstanbul", True),
        (KOMUNITE, IN_PERSON, "İstanbul", True),
        (KOMUNITE + " ve online (Zoom)", HYBRID, "İstanbul", True),
        ("Şişhane", IN_PERSON, "İstanbul", True),
        ("Şişli", IN_PERSON, "İstanbul", True),
        ("Kayışdağı", IN_PERSON, "İstanbul", True),
        ("Küçükçekmece", IN_PERSON, "İstanbul", True),
        ("İstanbul", IN_PERSON, "İstanbul", True),
        # Truncated by the source and no named city: never guessed.
        ("BÜ Güney Kampüs Demir Demirg...", IN_PERSON, None, True),
        ("Boğaziçi Üniversitesi Garant...", IN_PERSON, None, True),
        ("Hacettepe Ünivesitesi Beytep...", IN_PERSON, None, True),
    ],
)
def test_live_location_forms(raw, attendance, city, has_venue):
    info = parse_location(raw)
    assert (info.attendance, info.city) == (attendance, city)
    assert (info.venue is not None) is has_venue


@pytest.mark.parametrize("raw", [None, "", "   ", "-"])
def test_empty_location_is_unknown(raw):
    assert parse_location(raw) == LocationInfo()


@pytest.mark.parametrize(
    ("raw", "attendance"),
    [
        ("Online Etkinlik", ONLINE),
        ("Çevrimiçi", ONLINE),
        ("Çevrim içi", ONLINE),
        ("Uzaktan", ONLINE),
        ("Online / Ankara", HYBRID),
        ("Hybrid", HYBRID),
    ],
)
def test_attendance_variants(raw, attendance):
    assert parse_location(raw).attendance == attendance


@pytest.mark.parametrize(
    ("raw", "city"),
    [
        ("Ankara ODTÜ CoZone", "Ankara"),
        ("Çankaya, Ankara", "Ankara"),
        ("Bornova", "İzmir"),
        ("ELAZIĞ", "Elazığ"),
        ("elazig", "Elazığ"),
        ("Iğdır Üniversitesi", "Iğdır"),
        ("Hakkari", "Hakkâri"),
        ("Van", "Van"),
        ("Ordu", "Ordu"),
    ],
)
def test_city_from_named_province_or_district(raw, city):
    assert parse_location(raw).city == city


@pytest.mark.parametrize(
    "raw",
    [
        "Van Gogh Sergisi",  # English/Dutch name, not the province
        "Ordu Evi Konferans Salonu",  # "army house", not the province
        "Selçuk Üniversitesi",  # Konya, not the İzmir district; not mapped
        "İstanbul - Ankara",  # two cities: ambiguous
        "Koç Üniversitesi",  # university, no named city
    ],
)
def test_no_city_when_not_certain(raw):
    assert parse_location(raw).city is None


def test_there_are_81_distinct_provinces():
    assert len(set(PROVINCES)) == 81


def test_event_model_derives_fields_from_location():
    event = Event(
        title="t",
        url="https://x.test/1",
        source="s",
        location="Hibrit ( Istanbul & Zoom )",
    )
    assert (event.city, event.attendance) == ("İstanbul", HYBRID)

    event.location = "Online"
    assert (event.city, event.attendance, event.venue) == (None, ONLINE, None)

    event.location = None
    assert (event.city, event.attendance, event.venue) == (None, None, None)
