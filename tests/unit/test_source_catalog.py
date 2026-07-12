from app.services.source_catalog import SOURCE_CATALOG, get_enabled_sources, get_source


def test_source_catalog_has_unique_keys_and_names():
    assert len(SOURCE_CATALOG) == 10
    assert len({source.key for source in SOURCE_CATALOG}) == len(SOURCE_CATALOG)
    assert len({source.name for source in SOURCE_CATALOG}) == len(SOURCE_CATALOG)


def test_source_catalog_includes_tech_istanbul():
    source = get_source("tech-istanbul")

    assert source is not None
    assert source.name == "Tech Istanbul"
    assert source.mode == "static"


def test_source_catalog_resolves_legacy_akbank_name_to_canonical_source():
    source = get_source("Akbank")

    assert source is not None
    assert source.name == "Akbank Gençlik Akademisi"


def test_get_source_accepts_canonical_name_case_insensitively():
    source = get_source("TECH ISTANBUL")

    assert source is not None
    assert source.key == "tech-istanbul"


def test_enabled_sources_preserve_static_then_browser_order():
    sources = get_enabled_sources()
    modes = [source.mode for source in sources]

    assert modes == sorted(modes, key={"static": 0, "browser": 1}.get)
