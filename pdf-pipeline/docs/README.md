# PDF Pipeline (Discord + Indexed HTML)

This starter sets up a shared PDF intake/output structure for OpenClaw agents.

## Goals

- Store input PDFs and parsed outputs in a predictable folder structure
- Generate a clickable `index.html` for humans
- Keep machine-readable metadata in `manifest.json`
- Make outputs easy for agents to digest (`parsed.md`, `parsed.json`)

## Folder structure

```
pdf-pipeline/
  storage/
    index.html
    docs/
      <doc-id>/
        original.pdf
        parsed.md
        parsed.json
        summary.md
        manifest.json
  scripts/
    rebuild_index.py
```

## Document ID

Use a stable slug such as:

`2026-03-18-report-name`

## Minimal manifest schema

```json
{
  "docId": "2026-03-18-report-name",
  "title": "Report Name",
  "uploadedAt": "2026-03-18T15:00:00Z",
  "uploadedBy": "discord:dom_ds",
  "sourceChannel": "1483854530042134658",
  "tags": ["research", "iran"],
  "files": {
    "original": "original.pdf",
    "markdown": "parsed.md",
    "json": "parsed.json",
    "summary": "summary.md"
  },
  "parser": {
    "name": "opendataloader-pdf",
    "mode": "hybrid",
    "version": "TBD"
  }
}
```

## Build/rebuild index

From workspace root:

```bash
python3 pdf-pipeline/scripts/rebuild_index.py
```

This scans `pdf-pipeline/storage/docs/*/manifest.json` and regenerates:

- `pdf-pipeline/storage/index.html`

## Hosting options

- Nginx static path (recommended)
- Caddy static site
- Any static file host behind Tailscale/VPN

## Discord posting convention

In your PDF intake channel, post:

- `DOC:<doc-id>`
- Link to HTML index (or direct doc folder URL)

Example:

`DOC:2026-03-18-report-name https://your-host/pdf-pipeline/index.html`
