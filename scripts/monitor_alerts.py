#!/usr/bin/env python3
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

try:
    import requests
except Exception:
    requests = None


STATE_FILE = Path(os.getenv("ALERT_STATE_FILE", ".alert_state.json"))
COMPOSE_CMD = os.getenv("ALERT_COMPOSE_CMD", "docker compose")
SERVICES = [s.strip() for s in os.getenv("ALERT_SERVICES", "backend,scraper,db").split(",") if s.strip()]
LOG_LINES = int(os.getenv("ALERT_LOG_LINES", "120"))
COOLDOWN_SECONDS = int(os.getenv("ALERT_COOLDOWN_SECONDS", "900"))
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()

KEYWORDS = [
    "ModuleNotFoundError",
    "OperationalError",
    "password authentication failed",
    "App failed to load",
    "Failed to find attribute",
    "Traceback",
    "ERROR",
    "exited with code",
]


def run(cmd: str) -> tuple[int, str, str]:
    p = subprocess.run(cmd, shell=True, text=True, capture_output=True)
    return p.returncode, p.stdout.strip(), p.stderr.strip()


def load_state() -> dict:
    if not STATE_FILE.exists():
        return {"last_sent": {}}
    try:
        return json.loads(STATE_FILE.read_text())
    except Exception:
        return {"last_sent": {}}


def save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=True))


def send_telegram(text: str) -> bool:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("[WARN] TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID eksik, mesaj atilamadi.")
        print(text)
        return False
    if requests is None:
        print("[WARN] requests paketi yok, mesaj atilamadi.")
        print(text)
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "disable_web_page_preview": True,
    }
    try:
        r = requests.post(url, json=payload, timeout=10)
        ok = r.status_code == 200
        if not ok:
            print(f"[WARN] Telegram API hata: {r.status_code} {r.text}")
        return ok
    except Exception as exc:
        print(f"[WARN] Telegram gonderim hatasi: {exc}")
        return False


def parse_ps() -> list[dict]:
    code, out, err = run(f"{COMPOSE_CMD} ps --format json")
    if code != 0:
        print(f"[WARN] compose ps okunamadi: {err or out}")
        return []

    # docker compose json output can be array or json-lines depending on version
    out = out.strip()
    if not out:
        return []

    try:
        data = json.loads(out)
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            return [data]
    except Exception:
        pass

    items = []
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            items.append(json.loads(line))
        except Exception:
            continue
    return items


def collect_issues() -> list[str]:
    issues: list[str] = []
    ps = parse_ps()
    wanted = set(SERVICES)

    for row in ps:
        service = row.get("Service") or row.get("Name", "")
        if not service:
            continue
        # normalize container name into service guess if needed
        if service not in wanted:
            for s in wanted:
                if s in service:
                    service = s
                    break
        if service not in wanted:
            continue

        state = (row.get("State") or "").lower()
        health = (row.get("Health") or "").lower()
        status = row.get("Status") or ""
        if state not in {"running"}:
            issues.append(f"Servis ayakta degil: {service} | state={state or '-'} | status={status or '-'}")
        if health and health not in {"healthy"}:
            issues.append(f"Servis sagliksiz: {service} | health={health} | status={status or '-'}")

    for service in SERVICES:
        code, logs, _ = run(f"{COMPOSE_CMD} logs --no-color --tail={LOG_LINES} {service}")
        if code != 0:
            continue
        lines = [ln for ln in logs.splitlines() if any(k in ln for k in KEYWORDS)]
        if lines:
            tail = "\n".join(lines[-8:])
            issues.append(f"{service} log alarmi:\n{tail}")

    return issues


def issue_signature(issues: list[str]) -> str:
    raw = "\n\n".join(issues)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def main() -> int:
    state = load_state()
    last_sent = state.get("last_sent", {})
    now = int(time.time())

    issues = collect_issues()
    if not issues:
        print("[OK] Alarm yok")
        return 0

    sig = issue_signature(issues)
    prev = last_sent.get(sig, 0)
    if now - int(prev) < COOLDOWN_SECONDS:
        print("[INFO] Ayni alarm cooldown suresinde, mesaj gonderilmedi")
        return 0

    text = (
        "TechEventRadar Alarm\n"
        f"Zaman: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        + "\n\n".join(issues)
    )

    sent = send_telegram(text)
    if sent:
        last_sent[sig] = now
        state["last_sent"] = last_sent
        save_state(state)
        print("[OK] Alarm mesaji gonderildi")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
