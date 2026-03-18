# Discord Flow (PDF Intake → Agent Digest)

## Channels

- `#pdf-intake` (human uploads + ingestion notices)
- `#pdf-library` (index link + doc registry announcements)

## Operator flow

1. Save incoming PDF to a local temp path.
2. Run ingestion script:

```bash
python3 pdf-pipeline/scripts/ingest_pdf.py \
  --input "/path/to/input.pdf" \
  --title "My Report Title" \
  --uploaded-by "discord:dom_ds" \
  --source-channel "1483854530042134658" \
  --tags "research,policy"
```

3. Script output includes `docId` and regenerates `pdf-pipeline/storage/index.html`.
4. Post to Discord:

```text
DOC:<doc-id>
Library: <https://YOUR-HOST/pdf-pipeline/index.html>
Doc folder: <https://YOUR-HOST/pdf-pipeline/docs/<doc-id>/>
```

## Agent consumption convention

- Use `DOC:<doc-id>` as the reference key in prompts.
- Prefer `parsed.md` for summarization and synthesis.
- Use `parsed.json` when page coordinates/citations are required.

## Suggested governance

- Keep all docs immutable after ingest; write derived outputs as new files.
- Track parser mode/version in each `manifest.json`.
- Re-run `rebuild_index.py` after any manifest update.
