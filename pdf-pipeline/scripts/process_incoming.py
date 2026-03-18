#!/usr/bin/env python3
"""
Process PDFs dropped into pdf-pipeline/incoming and ingest them automatically.

Outputs a Discord-ready message file to pdf-pipeline/outbox/<doc-id>.txt
so operators can paste into #pdf-library.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INCOMING = ROOT / "incoming"
PROCESSED = ROOT / "processed"
OUTBOX = ROOT / "outbox"
INGEST = ROOT / "scripts" / "ingest_pdf.py"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_ingest(pdf_path: Path, uploaded_by: str, source_channel: str, tags: str) -> dict:
    title = pdf_path.stem.replace("_", " ").replace("-", " ").strip() or "Untitled PDF"
    cmd = [
        "python3",
        str(INGEST),
        "--input",
        str(pdf_path),
        "--title",
        title,
        "--uploaded-by",
        uploaded_by,
        "--source-channel",
        source_channel,
    ]
    if tags:
        cmd.extend(["--tags", tags])

    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        return {"ok": False, "error": (proc.stderr or proc.stdout).strip()}

    try:
        payload = json.loads(proc.stdout)
        return payload
    except Exception:
        return {"ok": False, "error": "Failed to parse ingest output", "raw": proc.stdout}


def write_outbox(doc_id: str, base_url: str):
    OUTBOX.mkdir(parents=True, exist_ok=True)
    if base_url:
        base = base_url.rstrip("/")
        index_url = f"{base}/index.html"
        doc_url = f"{base}/docs/{doc_id}/"
    else:
        index_url = "<SET_BASE_URL>/index.html"
        doc_url = f"<SET_BASE_URL>/docs/{doc_id}/"

    content = (
        f"DOC:{doc_id}\n"
        f"Library: <{index_url}>\n"
        f"Doc folder: <{doc_url}>\n"
    )
    (OUTBOX / f"{doc_id}.txt").write_text(content, encoding="utf-8")


def move_to_processed(pdf_path: Path, ok: bool):
    PROCESSED.mkdir(parents=True, exist_ok=True)
    suffix = ".ok" if ok else ".error"
    target = PROCESSED / f"{pdf_path.stem}-{int(time.time())}{suffix}{pdf_path.suffix.lower()}"
    shutil.move(str(pdf_path), str(target))


def process_once(uploaded_by: str, source_channel: str, tags: str, base_url: str) -> int:
    INCOMING.mkdir(parents=True, exist_ok=True)
    pdfs = sorted([p for p in INCOMING.iterdir() if p.is_file() and p.suffix.lower() == ".pdf"])
    if not pdfs:
        print("No PDFs found in incoming/")
        return 0

    for pdf in pdfs:
        print(f"[{utc_now()}] Processing {pdf.name}")
        result = run_ingest(pdf, uploaded_by=uploaded_by, source_channel=source_channel, tags=tags)
        ok = bool(result.get("ok"))
        if ok:
            doc_id = result.get("docId", "unknown-doc")
            write_outbox(doc_id, base_url=base_url)
            print(f"  -> OK docId={doc_id}")
        else:
            print(f"  -> ERROR {result.get('error', 'unknown')}" )
        move_to_processed(pdf, ok=ok)

    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--uploaded-by", default="discord:operator")
    ap.add_argument("--source-channel", default="")
    ap.add_argument("--tags", default="")
    ap.add_argument("--base-url", default="", help="Hosted base URL for pdf-pipeline/storage")
    ap.add_argument("--watch", action="store_true", help="Continuously watch incoming folder")
    ap.add_argument("--interval", type=int, default=30, help="Watch interval seconds")
    args = ap.parse_args()

    if not args.watch:
        return process_once(args.uploaded_by, args.source_channel, args.tags, args.base_url)

    print(f"Watching incoming/ every {args.interval}s")
    while True:
        process_once(args.uploaded_by, args.source_channel, args.tags, args.base_url)
        time.sleep(max(5, args.interval))


if __name__ == "__main__":
    raise SystemExit(main())
