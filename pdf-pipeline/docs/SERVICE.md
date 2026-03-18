# PDF Pipeline Watcher Service

The incoming watcher is installed as a user systemd service:

- Unit: `~/.config/systemd/user/pdf-pipeline-watcher.service`
- Env file: `pdf-pipeline/.env`

## Common commands

```bash
systemctl --user status pdf-pipeline-watcher.service
systemctl --user restart pdf-pipeline-watcher.service
systemctl --user stop pdf-pipeline-watcher.service
systemctl --user start pdf-pipeline-watcher.service
journalctl --user -u pdf-pipeline-watcher.service -n 100 --no-pager
```

## Update runtime settings

Edit:

- `pdf-pipeline/.env`

Then restart service:

```bash
systemctl --user restart pdf-pipeline-watcher.service
```
