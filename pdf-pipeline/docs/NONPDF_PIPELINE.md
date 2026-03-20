# Non-PDF Secondary Parser Pipeline (MarkItDown)

This is a separate process from the PDF pipeline and targets non-PDF files.

## Overview

- Intake source: dedicated Discord channel (configure channel id)
- Poller downloads non-PDF attachments to: `pdf-pipeline/nonpdf/incoming/`
- Watcher ingests + parses with MarkItDown
- Output lands in the same shared library index: `pdf-pipeline/storage/index.html`

## Scripts

- `scripts/discord_intake_poller_nonpdf.py`
- `scripts/process_incoming_nonpdf.py`
- `scripts/ingest_nonpdf.py`

## Services

- `pdf-nonpdf-intake-poller.service`
- `pdf-nonpdf-watcher.service`

## Config files

- `pdf-pipeline/.discord-intake-nonpdf.env`
  - `INTAKE_NONPDF_CHANNEL_ID=<your_channel_id>`
  - `DELETE_NONPDF_SOURCE_MESSAGE=true|false`

- `pdf-pipeline/.env-nonpdf`
  - runtime tags/source/base-url for watcher

## Enable intake poller after channel id is set

```bash
systemctl --user enable --now pdf-nonpdf-intake-poller.service
systemctl --user restart pdf-nonpdf-intake-poller.service
```

## Verify

```bash
systemctl --user status pdf-nonpdf-watcher.service
systemctl --user status pdf-nonpdf-intake-poller.service
journalctl --user -u pdf-nonpdf-intake-poller.service -n 100 --no-pager
```
