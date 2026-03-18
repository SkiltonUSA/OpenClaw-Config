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

## 3) Quick local test (no daemon)

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
