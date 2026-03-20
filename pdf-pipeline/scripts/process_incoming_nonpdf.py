#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INCOMING = ROOT / "nonpdf" / "incoming"
PROCESSED = ROOT / "nonpdf" / "processed"
OUTBOX = ROOT / "nonpdf" / "outbox"
INGEST = ROOT / "scripts" / "ingest_nonpdf.py"


def run_ingest(path: Path, uploaded_by: str, source_channel: str, tags: str) -> dict:
    title = path.stem.replace("_", " ").replace("-", " ").strip() or "Untitled"
    cmd = [
        "python3", str(INGEST),
        "--input", str(path),
        "--title", title,
        "--uploaded-by", uploaded_by,
        "--source-channel", source_channel,
    ]
    if tags:
        cmd.extend(["--tags", tags])
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        return {"ok": False, "error": (p.stderr or p.stdout).strip()}
    try:
        return json.loads(p.stdout)
    except Exception:
        return {"ok": False, "error": "Failed to parse ingest output", "raw": p.stdout}


def write_outbox(doc_id: str, base_url: str):
    OUTBOX.mkdir(parents=True, exist_ok=True)
    base = base_url.rstrip("/") if base_url else "<SET_BASE_URL>"
    content = (
        f"DOC:{doc_id}\n"
        f"Library: <{base}/index.html>\n"
        f"Doc folder: <{base}/docs/{doc_id}/>\n"
    )
    (OUTBOX / f"{doc_id}.txt").write_text(content, encoding="utf-8")


def move_processed(path: Path, ok: bool):
    if ok:
        path.unlink(missing_ok=True)
        return
    PROCESSED.mkdir(parents=True, exist_ok=True)
    target = PROCESSED / f"{path.stem}-{int(time.time())}.error{path.suffix.lower()}"
    shutil.move(str(path), str(target))


def process_once(uploaded_by: str, source_channel: str, tags: str, base_url: str):
    INCOMING.mkdir(parents=True, exist_ok=True)
    files = sorted([p for p in INCOMING.iterdir() if p.is_file()])
    if not files:
        print("No files found in nonpdf/incoming/")
        return 0

    for f in files:
        if f.suffix.lower() == ".pdf":
            continue
        result = run_ingest(f, uploaded_by, source_channel, tags)
        ok = bool(result.get("ok"))
        if ok:
            write_outbox(result.get("docId", "unknown-doc"), base_url)
        move_processed(f, ok)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--uploaded-by", default="discord:operator")
    ap.add_argument("--source-channel", default="")
    ap.add_argument("--tags", default="nonpdf")
    ap.add_argument("--base-url", default="")
    ap.add_argument("--watch", action="store_true")
    ap.add_argument("--interval", type=int, default=30)
    args = ap.parse_args()

    if not args.watch:
        return process_once(args.uploaded_by, args.source_channel, args.tags, args.base_url)

    while True:
        process_once(args.uploaded_by, args.source_channel, args.tags, args.base_url)
        time.sleep(max(5, args.interval))


if __name__ == "__main__":
    raise SystemExit(main())
