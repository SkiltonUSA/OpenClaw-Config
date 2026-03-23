# PDF Pipeline Services

## 1) Incoming watcher service

The incoming watcher is installed as a user systemd service:

- Unit: `~/.config/systemd/user/pdf-pipeline-watcher.service`
- Env file: `pdf-pipeline/.env`

Common commands:

```bash
systemctl --user status pdf-pipeline-watcher.service
systemctl --user restart pdf-pipeline-watcher.service
systemctl --user stop pdf-pipeline-watcher.service
systemctl --user start pdf-pipeline-watcher.service
journalctl --user -u pdf-pipeline-watcher.service -n 100 --no-pager
```

## 2) Library UI hosting service

A library server is installed to host the clickable index and delete API:

- Unit: `~/.config/systemd/user/pdf-pipeline-static.service`
- Script: `pdf-pipeline/scripts/library_server.py`
- Library URL: `http://127.0.0.1:8088/pdf-pipeline/storage/index.html`
- Delete endpoint: `POST /api/docs/<doc-id>/delete`

Common commands:

```bash
systemctl --user status pdf-pipeline-static.service
systemctl --user restart pdf-pipeline-static.service
systemctl --user stop pdf-pipeline-static.service
systemctl --user start pdf-pipeline-static.service
journalctl --user -u pdf-pipeline-static.service -n 100 --no-pager
```

## Update runtime settings

Edit:

- `pdf-pipeline/.env`

Then restart watcher:

```bash
systemctl --user restart pdf-pipeline-watcher.service
```
