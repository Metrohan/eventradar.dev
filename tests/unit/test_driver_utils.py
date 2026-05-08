import os
import sys
from unittest.mock import MagicMock, patch

os.environ.setdefault("ALLOW_INSECURE_DEFAULTS", "true")

_uc_mock = MagicMock()
_uc_mock.ChromeOptions = MagicMock
_uc_mock.Chrome = MagicMock
sys.modules.setdefault("undetected_chromedriver", _uc_mock)
os.environ.setdefault("SECRET_KEY", "test-secret-key-that-is-at-least-32-chars")
os.environ.setdefault("ADMIN_USERNAME", "testadmin")
os.environ.setdefault("ADMIN_PASSWORD", "testpassword")


def test_find_chromedriver_returns_none_when_cache_missing():
    from app.scrapers.driver_utils import find_chromedriver

    with patch("os.path.exists", return_value=False):
        assert find_chromedriver() is None


def test_find_chromedriver_returns_none_when_no_versions():
    from app.scrapers.driver_utils import find_chromedriver

    with patch("os.path.exists", return_value=True), patch(
        "os.listdir", return_value=[]
    ):
        assert find_chromedriver() is None


def test_find_chromedriver_returns_path_when_found(tmp_path):
    from app.scrapers.driver_utils import find_chromedriver

    driver_file = tmp_path / "114" / "chromedriver"
    driver_file.parent.mkdir(parents=True)
    driver_file.write_text("binary")

    with patch("os.path.expanduser", return_value=str(tmp_path)), patch(
        "os.path.exists", return_value=True
    ):
        result = find_chromedriver()

    assert result is not None
    assert result.endswith("chromedriver")


def test_find_chromedriver_returns_none_when_no_binary(tmp_path):
    from app.scrapers.driver_utils import find_chromedriver

    version_dir = tmp_path / "114"
    version_dir.mkdir(parents=True)
    (version_dir / "notes.txt").write_text("nothing here")

    with patch("os.path.expanduser", return_value=str(tmp_path)), patch(
        "os.path.exists", return_value=True
    ):
        result = find_chromedriver()

    assert result is None


def test_ensure_chromedriver_returns_existing_path():
    from app.scrapers.driver_utils import ensure_chromedriver

    with patch(
        "app.scrapers.driver_utils.find_chromedriver",
        return_value="/usr/bin/chromedriver",
    ):
        result = ensure_chromedriver()

    assert result == "/usr/bin/chromedriver"


def test_ensure_chromedriver_installs_when_not_found():
    from app.scrapers.driver_utils import ensure_chromedriver

    mock_manager = MagicMock()
    mock_manager.return_value.install.return_value = "/cached/chromedriver"

    with patch(
        "app.scrapers.driver_utils.find_chromedriver",
        side_effect=[None, "/cached/chromedriver"],
    ), patch.dict(
        "sys.modules",
        {"webdriver_manager.chrome": MagicMock(ChromeDriverManager=mock_manager)},
    ):
        result = ensure_chromedriver()

    assert result == "/cached/chromedriver"


def test_ensure_chromedriver_returns_none_on_install_error():
    from app.scrapers.driver_utils import ensure_chromedriver

    with patch("app.scrapers.driver_utils.find_chromedriver", return_value=None), patch(
        "builtins.__import__", side_effect=ImportError("no webdriver_manager")
    ):
        result = ensure_chromedriver()

    assert result is None
