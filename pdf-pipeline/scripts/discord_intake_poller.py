#!/usr/bin/env python3
"""
Poll a Discord channel for PDF attachments and drop them into pdf-pipeline/incoming.
The existing watcher service ingests from incoming automatically.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from urllib.request import Request, urlopen

STATE_FILE = Path("/home/ubuntu/.openclaw/workspace/pdf-pipeline/.discord-intake-state.json")
INCOMING = Path("/home/ubuntu/.openclaw/workspace/pdf-pipeline/incoming")

TOKEN = os.getenv("DISCORD_BOT_TOKEN", "").strip()
CHANNEL_ID = os.getenv("INTAKE_CHANNEL_ID", "").strip()
POLL_SECONDS = int(os.getenv("INTAKE_POLL_SECONDS", "20"))

API_BASE = "https://discord.com/api/v10"


def api_get(path: str):
    req = Request(
        API_BASE + path,
        headers={
            "Authorization": f"Bot {TOKEN}",
            "User-Agent": "openclaw-pdf-intake/1.0",
        },
    )
    with urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def download(url: str, dst: Path):
    req = Request(url, headers={"User-Agent": "openclaw-pdf-intake/1.0"})
    with urlopen(req, timeout=60) as r:
        data = r.read()
    dst.write_bytes(data)


def load_state():
    if not STATE_FILE.exists():
        return {"last_message_id": None, "seen_attachments": []}
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {"last_message_id": None, "seen_attachments": []}


def save_state(st):
    STATE_FILE.write_text(json.dumps(st, indent=2), encoding="utf-8")


def safe_name(name: str) -> str:
    keep = "-_.() abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    out = "".join(c if c in keep else "_" for c in name)
    return out.strip() or "file.pdf"


def run_once():
    st = load_state()
    seen = set(st.get("seen_attachments", []))

    path = f"/channels/{CHANNEL_ID}/messages?limit=50"
    msgs = api_get(path)
    if not isinstance(msgs, list):
        return

    # oldest -> newest for deterministic state updates
    msgs_sorted = list(reversed(msgs))

    for m in msgs_sorted:
        mid = m.get("id")
        attachments = m.get("attachments", []) or []
        for a in attachments:
            fn = a.get("filename", "")
            url = a.get("url", "")
            aid = a.get("id", "")
            if not fn.lower().endswith(".pdf"):
                continue
            key = f"{mid}:{aid}:{fn}"
            if key in seen:
                continue

            INCOMING.mkdir(parents=True, exist_ok=True)
            out_name = safe_name(f"{mid}-{fn}")
            out_path = INCOMING / out_name
            download(url, out_path)
            print(f"Downloaded PDF -> {out_path}")
            seen.add(key)

        if mid:
            st["last_message_id"] = mid

    # prevent unbounded growth
    st["seen_attachments"] = list(seen)[-5000:]
    save_state(st)


def main():
    if not TOKEN or not CHANNEL_ID:
        raise SystemExit("DISCORD_BOT_TOKEN and INTAKE_CHANNEL_ID are required")

    while True:
        try:
            run_once()
        except Exception as e:
            print(f"poll error: {e}")
        time.sleep(max(POLL_SECONDS, 5))


if __name__ == "__main__":
    main()
