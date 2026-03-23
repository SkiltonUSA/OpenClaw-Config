# Hosting the PDF Library Index (Clickable HTML)

This guide serves `pdf-pipeline/storage/` as static files.

## 1) Nginx (recommended)

Example server block snippet:

```nginx
server {
  listen 8088;
  server_name _;

  location /pdf-pipeline/ {
    alias /home/ubuntu/.openclaw/workspace/pdf-pipeline/storage/;
    autoindex on;
    index index.html;
  }
}
```

Then:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

Library URL:

- `http://<host>:8088/pdf-pipeline/index.html`

## 2) Caddy

```caddy
:8088 {
  handle /pdf-pipeline/* {
    root * /home/ubuntu/.openclaw/workspace/pdf-pipeline/storage
    file_server
  }
}
```

## 3) Built-in library server (recommended for delete UI)

Use the bundled server that supports both static files and delete API:

```bash
python3 /home/ubuntu/.openclaw/workspace/pdf-pipeline/scripts/library_server.py
```

Open:

- `http://<host>:8088/pdf-pipeline/storage/index.html`

Delete endpoint (used by UI):

- `POST /api/docs/<doc-id>/delete`

## 4) Quick local static test (read-only)

```bash
cd /home/ubuntu/.openclaw/workspace/pdf-pipeline/storage
python3 -m http.server 8088
```

Open:

- `http://<host>:8088/index.html`

## Security notes

- Prefer exposing only over Tailscale/VPN.
- Do not expose sensitive PDFs publicly without access control.
- Consider basic auth at reverse proxy if needed.
