#!/usr/bin/env python3
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


def parse_with_markitdown(input_path: Path, output_dir: Path) -> dict:
    parser_meta = {
        "name": "markitdown",
        "mode": "local",
        "version": "unknown",
        "status": "skipped",
        "notes": "CLI not found",
    }

    local_cli = ROOT / ".venv-nonpdf" / "bin" / "markitdown"
    if local_cli.exists():
        cli = str(local_cli)
    else:
        which = run(["bash", "-lc", "command -v markitdown || true"]).stdout.strip()
        if not which:
            return parser_meta
        cli = which

    parser_meta["status"] = "attempted"
    ver = run([cli, "--version"]).stdout.strip()
    if ver:
        parser_meta["version"] = ver

    out_md = output_dir / "parsed.md"
    proc = run([cli, str(input_path), "-o", str(out_md)])
    if proc.returncode == 0 and out_md.exists():
        parser_meta["status"] = "ok"
        parser_meta["notes"] = "Parsed with markitdown"
    else:
        parser_meta["status"] = "error"
        parser_meta["notes"] = (proc.stderr or proc.stdout or "unknown parser error").strip()[:400]

    return parser_meta


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Path to source file")
    ap.add_argument("--title", required=True)
    ap.add_argument("--uploaded-by", default="discord:unknown")
    ap.add_argument("--source-channel", default="")
    ap.add_argument("--tags", default="")
    ap.add_argument("--doc-id", default="")
    args = ap.parse_args()

    src = Path(args.input).expanduser().resolve()
    if not src.exists():
        raise SystemExit(f"Input must exist: {src}")

    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    if args.doc_id:
        doc_id = slugify(args.doc_id)
    else:
        date_prefix = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        doc_id = f"{date_prefix}-{slugify(args.title)}"

    doc_dir = DOCS_DIR / doc_id
    doc_dir.mkdir(parents=True, exist_ok=True)

    ext = src.suffix.lower() or ".bin"
    original_name = f"original{ext}"
    dst = doc_dir / original_name
    shutil.copy2(src, dst)

    parsed_md = doc_dir / "parsed.md"
    parsed_json = doc_dir / "parsed.json"
    summary_md = doc_dir / "summary.md"
    if not parsed_md.exists():
        parsed_md.write_text("# Parsed Markdown\n\nPending parser output.\n", encoding="utf-8")
    if not parsed_json.exists():
        parsed_json.write_text("{}\n", encoding="utf-8")
    if not summary_md.exists():
        summary_md.write_text("# Summary\n\nPending summary generation.\n", encoding="utf-8")

    parser_meta = parse_with_markitdown(dst, doc_dir)

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

    if parser_meta.get("status") == "ok" and dst.exists():
        dst.unlink(missing_ok=True)
        manifest["files"]["original"] = None
        manifest["retention"] = {"originalDeleted": True, "deletedAt": utc_now_iso()}

    (doc_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    run(["python3", str(REBUILD_SCRIPT)])

    print(json.dumps({"ok": True, "docId": doc_id, "docDir": str(doc_dir), "parser": parser_meta}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
