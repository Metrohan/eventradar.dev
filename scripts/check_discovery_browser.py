"""Run real-backend browser discovery checks using only a fresh temporary SQLite DB.
Requires Python requirements-dev, frontend npm ci/build and installed Chromium.
Never connects to production; all child servers bind loopback and are stopped.
"""

import os
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from datetime import timedelta
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def ready(url):
    for _ in range(60):
        try:
            with urlopen(url, timeout=1):
                return
        except OSError:
            time.sleep(0.2)
    raise RuntimeError("Local test server did not start")


def main():
    with tempfile.TemporaryDirectory(prefix="eventradar-discovery-") as temp:
        os.environ.update(
            DATABASE_URL="sqlite:///" + temp + "/events.db",
            THUMBNAIL_DIR=temp + "/thumbnails",
            ALLOW_INSECURE_DEFAULTS="true",
            SECRET_KEY="synthetic-discovery-test-secret-32-chars",
            ADMIN_USERNAME="synthetic-test-admin",
            ADMIN_PASSWORD="synthetic-test-password",
        )
        from app.core.database import Base, engine, SessionLocal
        import app.models  # noqa: F401
        from app.models.event import Event
        from app.utils.event_dates import local_now
        from app.services.tag_service import seed_tags
        from app.models.tag import Tag

        Base.metadata.create_all(engine)
        with SessionLocal() as db:
            seed_tags(db)
            event = Event(
                title="İstanbul Python Atölyesi",
                description="<script>evil()</script>",
                date=local_now() + timedelta(days=10),
                location="İstanbul",
                url="https://example.org/event",
                source="Synthetic",
            )
            event.tags = [db.query(Tag).filter(Tag.name == "atolye").one()]
            db.add(event)
            db.add(
                Event(
                    title="Hidden",
                    slug="hidden-test-event",
                    url="https://example.org/hidden",
                    source="Synthetic",
                    is_active=False,
                    deactivation_reason="manual",
                )
            )
            db.commit()
            slug = event.slug
        backend_port, frontend_port = free_port(), free_port()
        env = os.environ.copy()
        env.update(
            VITE_PREVIEW_API_TARGET=f"http://127.0.0.1:{backend_port}",
            PLAYWRIGHT_BASE_URL=f"http://127.0.0.1:{frontend_port}",
            PLAYWRIGHT_NO_WEBSERVER="1",
            SSR_EVENT_SLUG=slug,
        )
        processes = []
        with open(Path(temp) / "server.log", "w") as output:
            try:
                processes.append(
                    subprocess.Popen(
                        [
                            sys.executable,
                            "-m",
                            "uvicorn",
                            "app.main:app",
                            "--host",
                            "127.0.0.1",
                            "--port",
                            str(backend_port),
                        ],
                        cwd=ROOT,
                        env=env,
                        stdout=output,
                        stderr=output,
                    )
                )
                ready(f"http://127.0.0.1:{backend_port}/health")
                processes.append(
                    subprocess.Popen(
                        [
                            "npm",
                            "--prefix",
                            "frontend",
                            "run",
                            "preview",
                            "--",
                            "--host",
                            "127.0.0.1",
                            "--port",
                            str(frontend_port),
                            "--strictPort",
                        ],
                        cwd=ROOT,
                        env=env,
                        stdout=output,
                        stderr=output,
                    )
                )
                ready(env["PLAYWRIGHT_BASE_URL"])
                result = subprocess.run(
                    [
                        "npm",
                        "--prefix",
                        "frontend",
                        "run",
                        "test:hydration",
                        "--",
                        "discovery.spec.js",
                    ],
                    cwd=ROOT,
                    env=env,
                    check=False,
                )
                if result.returncode:
                    raise RuntimeError("Discovery browser checks failed")
            finally:
                for process in reversed(processes):
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait()
        engine.dispose()


if __name__ == "__main__":
    main()
