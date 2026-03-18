# Discord Intake Automation

This automation watches a Discord channel for PDF attachments and drops them into:

- `pdf-pipeline/incoming/`

Then `pdf-pipeline-watcher.service` ingests and indexes automatically.

## Service

- Unit: `~/.config/systemd/user/pdf-intake-poller.service`
- Script: `pdf-pipeline/scripts/discord_intake_poller.py`
- Env file (contains bot token): `pdf-pipeline/.discord-intake.env`

## Configure intake channel

Edit `pdf-pipeline/.discord-intake.env`:

```bash
INTAKE_CHANNEL_ID=<your-channel-id>
```

Then restart:

```bash
systemctl --user restart pdf-intake-poller.service
```

## Commands

```bash
systemctl --user status pdf-intake-poller.service
systemctl --user restart pdf-intake-poller.service
journalctl --user -u pdf-intake-poller.service -n 100 --no-pager
```

## Retention policy

- On successful ingest, source PDF in `incoming/` is deleted.
- On successful parse, `original.pdf` in document storage is deleted (parsed artifacts retained).
- Intake poller can delete the original Discord message after attachment download when:
  - `DELETE_SOURCE_MESSAGE=true` in `.discord-intake.env`
  - bot has message delete permissions in the intake channel

## Important

- If channel creation is blocked by Discord permissions, create the intake channel manually in Discord and provide its channel ID.
- Rotate bot tokens if they are ever pasted in chat.
