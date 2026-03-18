#!/usr/bin/env python3
import json
from pathlib import Path
from html import escape
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
STORAGE = ROOT / "storage"
DOCS_DIR = STORAGE / "docs"
INDEX = STORAGE / "index.html"


def load_manifest(p: Path):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def row_for_manifest(m: dict):
    doc_id = m.get("docId", "unknown")
    title = m.get("title", doc_id)
    uploaded_at = m.get("uploadedAt", "")
    uploaded_by = m.get("uploadedBy", "")
    tags = ", ".join(m.get("tags", []))
    files = m.get("files", {})

    base = f"docs/{escape(doc_id)}/"

    def lnk(name, label):
        if not name:
            return "-"
        return f'<a href="{base}{escape(name)}">{escape(label)}</a>'

    return {
        "docId": doc_id,
        "title": title,
        "uploadedAt": uploaded_at,
        "uploadedBy": uploaded_by,
        "tags": tags,
        "original": lnk(files.get("original"), "original.pdf"),
        "markdown": lnk(files.get("markdown"), "parsed.md"),
        "json": lnk(files.get("json"), "parsed.json"),
        "summary": lnk(files.get("summary"), "summary.md"),
    }


def main():
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    manifests = []
    for manifest_path in DOCS_DIR.glob("*/manifest.json"):
        m = load_manifest(manifest_path)
        if m:
            manifests.append(row_for_manifest(m))

    manifests.sort(key=lambda x: x.get("uploadedAt", ""), reverse=True)

    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    rows = []
    for r in manifests:
        rows.append(
            "<tr>"
            f"<td>{escape(r['docId'])}</td>"
            f"<td>{escape(r['title'])}</td>"
            f"<td>{escape(r['uploadedAt'])}</td>"
            f"<td>{escape(r['uploadedBy'])}</td>"
            f"<td>{escape(r['tags'])}</td>"
            f"<td>{r['original']}</td>"
            f"<td>{r['markdown']}</td>"
            f"<td>{r['json']}</td>"
            f"<td>{r['summary']}</td>"
            "</tr>"
        )

    table_rows = "\n".join(rows) if rows else (
        "<tr><td colspan='9'><em>No documents indexed yet.</em></td></tr>"
    )

    html = f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>PDF Pipeline Index</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; }}
    h1 {{ margin-bottom: 8px; }}
    .meta {{ color: #555; margin-bottom: 16px; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; vertical-align: top; }}
    th {{ background: #f5f5f5; }}
    tr:nth-child(even) {{ background: #fafafa; }}
    a {{ text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
  </style>
</head>
<body>
  <h1>PDF Pipeline Index</h1>
  <div class=\"meta\">Generated: {escape(generated)}</div>
  <table>
    <thead>
      <tr>
        <th>Doc ID</th>
        <th>Title</th>
        <th>Uploaded</th>
        <th>By</th>
        <th>Tags</th>
        <th>Original</th>
        <th>Markdown</th>
        <th>JSON</th>
        <th>Summary</th>
      </tr>
    </thead>
    <tbody>
      {table_rows}
    </tbody>
  </table>
</body>
</html>
"""

    INDEX.write_text(html, encoding="utf-8")
    print(f"Wrote: {INDEX}")


if __name__ == "__main__":
    main()
