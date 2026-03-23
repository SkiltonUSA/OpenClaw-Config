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
    tags = m.get("tags", [])
    files = m.get("files", {})

    base = f"docs/{escape(doc_id)}/"

    def lnk(name, label):
        if not name:
            return ""
        return f'<a class="chip" href="{base}{escape(name)}" target="_blank" rel="noopener">{escape(label)}</a>'

    return {
        "docId": doc_id,
        "title": title,
        "uploadedAt": uploaded_at,
        "uploadedBy": uploaded_by,
        "tags": tags,
        "tagsText": ", ".join(tags),
        "original": lnk(files.get("original"), "original"),
        "markdown": lnk(files.get("markdown"), "markdown"),
        "json": lnk(files.get("json"), "json"),
        "summary": lnk(files.get("summary"), "summary"),
        "docUrl": f"docs/{escape(doc_id)}/",
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

    cards = []
    for r in manifests:
        tag_html = "".join([f'<span class="tag">{escape(t)}</span>' for t in r["tags"]])
        file_links = " ".join([x for x in [r["original"], r["markdown"], r["json"], r["summary"]] if x]) or "<span class='muted'>no files</span>"
        cards.append(
            f"""
<article class="card" data-doc-id="{escape(r['docId'])}" data-search="{escape((r['docId'] + ' ' + r['title'] + ' ' + r['uploadedBy'] + ' ' + r['tagsText']).lower())}">
  <div class="card-head">
    <div>
      <h3>{escape(r['title'])}</h3>
      <p class="docid">DOC:{escape(r['docId'])}</p>
    </div>
    <button class="danger" onclick="deleteDoc('{escape(r['docId'])}')">Delete</button>
  </div>
  <div class="meta-grid">
    <div><span>Uploaded</span><strong>{escape(r['uploadedAt'])}</strong></div>
    <div><span>By</span><strong>{escape(r['uploadedBy']) or '-'}</strong></div>
    <div><span>Folder</span><strong><a href="{r['docUrl']}" target="_blank" rel="noopener">open</a></strong></div>
  </div>
  <div class="tags">{tag_html or '<span class="muted">no tags</span>'}</div>
  <div class="files">{file_links}</div>
</article>
"""
        )

    cards_html = "\n".join(cards) if cards else "<div class='empty'>No documents indexed yet.</div>"

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Document Library</title>
  <style>
    :root {{ --bg:#0d1117; --panel:#161b22; --muted:#8b949e; --text:#e6edf3; --line:#30363d; --accent:#58a6ff; --danger:#f85149; }}
    * {{ box-sizing: border-box; }}
    body {{ margin:0; font-family: Inter, system-ui, Arial, sans-serif; background:var(--bg); color:var(--text); }}
    .wrap {{ max-width:1100px; margin:0 auto; padding:24px; }}
    .top {{ display:flex; justify-content:space-between; gap:12px; align-items:center; flex-wrap:wrap; }}
    h1 {{ margin:0; font-size:1.5rem; }}
    .muted {{ color:var(--muted); }}
    .meta {{ font-size:.9rem; color:var(--muted); }}
    .search {{ width:100%; margin-top:14px; background:var(--panel); border:1px solid var(--line); color:var(--text); border-radius:10px; padding:12px 14px; }}
    .grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(320px,1fr)); gap:14px; margin-top:18px; }}
    .card {{ background:var(--panel); border:1px solid var(--line); border-radius:14px; padding:14px; }}
    .card-head {{ display:flex; justify-content:space-between; gap:10px; align-items:flex-start; }}
    h3 {{ margin:0 0 2px; font-size:1rem; }}
    .docid {{ margin:0; font-size:.84rem; color:var(--muted); }}
    .meta-grid {{ display:grid; grid-template-columns:1fr 1fr 1fr; gap:8px; margin:12px 0; }}
    .meta-grid span {{ display:block; color:var(--muted); font-size:.74rem; }}
    .meta-grid strong {{ font-size:.85rem; }}
    .tags {{ display:flex; flex-wrap:wrap; gap:6px; margin-bottom:10px; min-height:24px; }}
    .tag {{ background:#1f2937; border:1px solid var(--line); border-radius:999px; padding:3px 9px; font-size:.75rem; }}
    .files {{ display:flex; flex-wrap:wrap; gap:8px; }}
    .chip {{ text-decoration:none; color:var(--accent); border:1px solid var(--line); border-radius:999px; padding:4px 10px; font-size:.78rem; }}
    .chip:hover {{ border-color:var(--accent); }}
    .danger {{ background:transparent; border:1px solid var(--danger); color:var(--danger); border-radius:8px; padding:6px 10px; cursor:pointer; font-size:.78rem; }}
    .danger:hover {{ background:rgba(248,81,73,.12); }}
    .empty {{ margin-top:16px; padding:20px; border:1px dashed var(--line); border-radius:12px; color:var(--muted); }}
    .status {{ margin-top:10px; font-size:.9rem; min-height:20px; }}
    .logbox {{ margin-top:18px; background:var(--panel); border:1px solid var(--line); border-radius:12px; padding:12px; }}
    .logbox h2 {{ margin:0 0 10px; font-size:1rem; }}
    .logitem {{ display:flex; justify-content:space-between; gap:10px; padding:8px 0; border-top:1px solid #222831; font-size:.85rem; }}
    .logitem:first-child {{ border-top:0; }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="top">
      <div>
        <h1>📚 Document Library</h1>
        <div class="meta">Generated: {escape(generated)}</div>
      </div>
      <div class="meta">Shared index for PDF + non-PDF pipelines</div>
    </div>

    <input id="search" class="search" type="search" placeholder="Search by title, doc id, uploader, tags..." oninput="filterCards()" />
    <div id="status" class="status muted"></div>

    <section id="grid" class="grid">
      {cards_html}
    </section>

    <section class="logbox">
      <h2>🗑️ Deletion Log</h2>
      <div id="deletions" class="muted">Loading…</div>
    </section>
  </div>

<script>
function filterCards() {{
  const q = document.getElementById('search').value.trim().toLowerCase();
  const cards = [...document.querySelectorAll('.card')];
  let shown = 0;
  cards.forEach(c => {{
    const s = c.dataset.search || '';
    const ok = !q || s.includes(q);
    c.style.display = ok ? '' : 'none';
    if (ok) shown++;
  }});
  document.getElementById('status').textContent = `Showing ${{shown}} document(s)`;
}}

async function deleteDoc(docId) {{
  if (!confirm(`Delete document ${{docId}}? This removes it from server storage.`)) return;
  const status = document.getElementById('status');
  status.textContent = `Deleting ${{docId}}...`;
  try {{
    const res = await fetch(`/api/docs/${{encodeURIComponent(docId)}}/delete`, {{ method: 'POST' }});
    const data = await res.json();
    if (!res.ok || !data.ok) throw new Error(data.error || 'Delete failed');
    const card = document.querySelector(`.card[data-doc-id="${{CSS.escape(docId)}}"]`);
    if (card) card.remove();
    status.textContent = `Deleted ${{docId}}`;
    filterCards();
  }} catch (e) {{
    status.textContent = `Delete failed: ${{e.message}}`;
  }}
}}

async function loadDeletions() {{
  const box = document.getElementById('deletions');
  try {{
    const res = await fetch('/api/deletions');
    const data = await res.json();
    if (!data.ok) throw new Error('failed');
    const items = data.items || [];
    if (!items.length) {{ box.innerHTML = '<span class="muted">No deletions logged yet.</span>'; return; }}
    box.innerHTML = items.slice(0,20).map(i =>
      '<div class="logitem"><span><strong>' + i.docId + '</strong></span><span class="muted">' + i.deletedAt + '</span></div>'
    ).join('');
  }} catch (e) {{
    box.textContent = 'Could not load deletion log.';
  }}
}}

filterCards();
loadDeletions();
</script>
</body>
</html>
"""

    INDEX.write_text(html, encoding="utf-8")
    print(f"Wrote: {INDEX}")


if __name__ == "__main__":
    main()
