#!/usr/bin/env python3
"""
Ingest a PDF into the shared pipeline storage and optionally parse it with opendataloader-pdf.

Example:
  python3 pdf-pipeline/scripts/ingest_pdf.py \
    --input /path/to/file.pdf \
    --title "Iran Research Brief" \
    --uploaded-by "discord:dom_ds" \
    --source-channel "1483854530042134658" \
    --tags research,iran
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STORAGE = ROOT / "storage"
DOCS_DIR = STORAGE / "docs"
REBUILD_SCRIPT = ROOT / "scripts" / "rebuild_index.py"


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "document"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True)


def parse_with_opendataloader(input_pdf: Path, output_dir: Path) -> dict:
    """Attempt parsing into markdown + json using opendataloader-pdf CLI."""
    parser_meta = {
        "name": "opendataloader-pdf",
        "mode": "local",
        "version": "unknown",
        "status": "skipped",
        "notes": "CLI not found",
    }

    local_cli = ROOT / ".venv" / "bin" / "opendataloader-pdf"
    if local_cli.exists():
        cli_cmd = [str(local_cli)]
    else:
        which = run(["bash", "-lc", "command -v opendataloader-pdf || true"])
        cli = which.stdout.strip()
        if not cli:
            return parser_meta
        cli_cmd = [cli]

    parser_meta["status"] = "attempted"
    version = run(cli_cmd + ["--version"]).stdout.strip()
    if version:
        parser_meta["version"] = version

    # Output directly inside doc folder.
    cmd = cli_cmd + [
        str(input_pdf),
        "-o",
        str(output_dir),
        "-f",
        "markdown,json",
    ]
    proc = run(cmd)
    if proc.returncode == 0:
        parser_meta["status"] = "ok"
        parser_meta["notes"] = "Parsed with local mode"
    else:
        parser_meta["status"] = "error"
        parser_meta["notes"] = (proc.stderr or proc.stdout or "unknown parser error").strip()[:400]

    return parser_meta


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Path to source PDF")
    ap.add_argument("--title", required=True, help="Document title")
    ap.add_argument("--uploaded-by", default="discord:unknown")
    ap.add_argument("--source-channel", default="")
    ap.add_argument("--tags", default="", help="Comma-separated tags")
    ap.add_argument("--doc-id", default="", help="Optional explicit doc id")
    args = ap.parse_args()

    src = Path(args.input).expanduser().resolve()
    if not src.exists() or src.suffix.lower() != ".pdf":
        raise SystemExit(f"Input must be an existing PDF: {src}")

    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    if args.doc_id:
        doc_id = slugify(args.doc_id)
    else:
        date_prefix = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        doc_id = f"{date_prefix}-{slugify(args.title)}"

    doc_dir = DOCS_DIR / doc_id
    doc_dir.mkdir(parents=True, exist_ok=True)

    original_name = "original.pdf"
    dst_pdf = doc_dir / original_name
    shutil.copy2(src, dst_pdf)

    # Placeholder outputs (parser may overwrite/create real versions).
    parsed_md = doc_dir / "parsed.md"
    parsed_json = doc_dir / "parsed.json"
    summary_md = doc_dir / "summary.md"

    if not parsed_md.exists():
        parsed_md.write_text("# Parsed Markdown\n\nPending parser output.\n", encoding="utf-8")
    if not parsed_json.exists():
        parsed_json.write_text("{}\n", encoding="utf-8")
    if not summary_md.exists():
        summary_md.write_text("# Summary\n\nPending summary generation.\n", encoding="utf-8")

    parser_meta = parse_with_opendataloader(dst_pdf, doc_dir)

    # Normalize opendataloader outputs to parsed.md / parsed.json when available.
    generated_md = doc_dir / "original.md"
    generated_json = doc_dir / "original.json"
    if parser_meta.get("status") == "ok":
        if generated_md.exists():
            parsed_md.write_text(generated_md.read_text(encoding="utf-8"), encoding="utf-8")
        if generated_json.exists():
            parsed_json.write_text(generated_json.read_text(encoding="utf-8"), encoding="utf-8")

    tags = [t.strip() for t in args.tags.split(",") if t.strip()]
    manifest = {
        "docId": doc_id,
        "title": args.title,
        "uploadedAt": utc_now_iso(),
        "uploadedBy": args.uploaded_by,
        "sourceChannel": args.source_channel,
        "tags": tags,
        "files": {
            "original": original_name,
            "markdown": "parsed.md",
            "json": "parsed.json",
            "summary": "summary.md",
        },
        "parser": parser_meta,
    }

    # If parsing completed successfully, remove original PDF from server storage.
    if parser_meta.get("status") == "ok" and dst_pdf.exists():
        dst_pdf.unlink(missing_ok=True)
        manifest["files"]["original"] = None
        manifest["retention"] = {"originalDeleted": True, "deletedAt": utc_now_iso()}

    (doc_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    run(["python3", str(REBUILD_SCRIPT)])

    print(json.dumps({
        "ok": True,
        "docId": doc_id,
        "docDir": str(doc_dir),
        "index": str(STORAGE / "index.html"),
        "parser": parser_meta,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
