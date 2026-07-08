import os
import subprocess


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
                os.chmod(driver_path, 0o750)  # nosec B103
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


def get_chrome_major_version() -> int | None:
    """Sunucuda kurulu Chrome'un ana sürüm numarasını döner (örn. 148)."""
    try:
        out = subprocess.check_output(
            ["google-chrome", "--version"], stderr=subprocess.DEVNULL, text=True
        )
        version_str = out.strip().split()[-1]
        return int(version_str.split(".")[0])
    except Exception:
        return None


def create_uc_driver(options=None):
    """undetected_chromedriver.Chrome başlatır; kurulu Chrome sürümünü otomatik
    tespit edip ``version_main``'e verir. Sabit bir sürüm numarası kodda
    hardcode edilmez, çünkü sunucudaki Chrome otomatik güncellendiğinde
    (ör. undetected-chromedriver ile Chrome sürümü uyuşmazlığı) scraper'lar
    sessizce kırılırdı."""
    import undetected_chromedriver as uc

    version = get_chrome_major_version()
    kwargs = {"use_subprocess": True}
    if options:
        kwargs["options"] = options
    if version:
        kwargs["version_main"] = version
    return uc.Chrome(**kwargs)
