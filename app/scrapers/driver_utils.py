import os


def find_chromedriver() -> str | None:
    """webdriver-manager cache'inden ChromeDriver binary'yi bulur."""
    cache_dir = os.path.expanduser("~/.wdm/drivers/chromedriver")
    if not os.path.exists(cache_dir):
        return None
    versions = os.listdir(cache_dir)
    if not versions:
        return None
    latest = sorted(versions)[-1]
    driver_dir = os.path.join(cache_dir, latest)
    for root, _dirs, files in os.walk(driver_dir):
        for file in files:
            if file in ("chromedriver", "chromedriver.exe"):
                driver_path = os.path.join(root, file)
                os.chmod(driver_path, 0o755)
                return driver_path
    return None


def ensure_chromedriver() -> str | None:
    """ChromeDriver'ı bulur; yoksa webdriver-manager ile indirir."""
    path = find_chromedriver()
    if path:
        return path
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        ChromeDriverManager().install()
        return find_chromedriver()
    except Exception as e:
        print(f"ChromeDriver indirilemedi: {e}")
        return None
