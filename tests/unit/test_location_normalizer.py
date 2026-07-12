import pytest

from app.services.location_normalizer import normalize_location


@pytest.mark.parametrize(
    "value",
    ["Online", " online ", "ONLINE ETKİNLİK", "Çevrimiçi", "remote", "Uzaktan"],
)
def test_online_variants_are_canonical(value):
    assert normalize_location(value) == "Online"


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("Istanbul", "İstanbul"),
        ("İSTANBUL", "İstanbul"),
        ("Izmir", "İzmir"),
        ("Eskisehir", "Eskişehir"),
        ("Elazig", "Elazığ"),
    ],
)
def test_city_variants_are_canonical(value, expected):
    assert normalize_location(value) == expected


def test_specific_venue_or_district_is_preserved():
    assert normalize_location("  Küçükçekmece   Kampüsü ") == "Küçükçekmece Kampüsü"


@pytest.mark.parametrize("value", [None, "", "   ", "-"])
def test_missing_location_returns_none(value):
    assert normalize_location(value) is None
