#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import subprocess
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import unquote
from datetime import datetime, timezone

MONITORED_SERVICES = [
    'openclaw-gateway.service',
    'pdf-pipeline-watcher.service',
    'pdf-intake-poller.service',
    'pdf-nonpdf-watcher.service',
    'pdf-nonpdf-intake-poller.service',
    'mark-deep-research-poller.service',
    'pdf-pipeline-static.service',
]

ROOT = Path('/home/ubuntu/.openclaw/workspace/pdf-pipeline/storage').resolve()
DOCS_DIR = (ROOT / 'docs').resolve()
REBUILD = Path('/home/ubuntu/.openclaw/workspace/pdf-pipeline/scripts/rebuild_index.py').resolve()
DELETE_LOG = Path('/home/ubuntu/.openclaw/workspace/pdf-pipeline/storage/deletions.jsonl').resolve()
PREFIX = '/pdf-pipeline/storage'


def safe_doc_id(doc_id: str) -> bool:
    return bool(re.fullmatch(r'[a-zA-Z0-9._-]+', doc_id))


def read_deletions(limit: int = 200):
    lines = []
    if DELETE_LOG.exists():
        for line in DELETE_LOG.read_text(encoding='utf-8').splitlines()[-limit:]:
            try:
                lines.append(json.loads(line))
            except Exception:
                pass
    return list(reversed(lines))


def get_service_status(name: str) -> str:
    p = subprocess.run(['systemctl', '--user', 'is-active', name], capture_output=True, text=True)
    return (p.stdout or p.stderr).strip() or 'unknown'


class Handler(SimpleHTTPRequestHandler):
    def translate_path(self, path: str) -> str:
        path = path.split('?', 1)[0]
        path = path.split('#', 1)[0]
        path = unquote(path)

        if path.startswith(PREFIX):
            rel = path[len(PREFIX):].lstrip('/')
        else:
            rel = path.lstrip('/')
        full = (ROOT / rel).resolve()

        if ROOT not in full.parents and full != ROOT:
            return str(ROOT)
        return str(full)

    def do_GET(self):
        if self.path in ('/', '/index.html'):
            self.send_response(302)
            self.send_header('Location', f'{PREFIX}/index.html')
            self.end_headers()
            return
        if self.path in ('/ops', '/ops-dashboard', '/ops-dashboard.html'):
            self.send_response(302)
            self.send_header('Location', f'{PREFIX}/ops-dashboard.html')
            self.end_headers()
            return
        if self.path.startswith('/api/deletions'):
            self._json(200, {'ok': True, 'items': read_deletions(200)})
            return
        if self.path.startswith('/api/ops/summary'):
            docs_count = len([p for p in DOCS_DIR.glob('*/manifest.json')])
            services = [{
                'name': s,
                'status': get_service_status(s),
            } for s in MONITORED_SERVICES]
            self._json(200, {
                'ok': True,
                'generatedAt': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
                'docsCount': docs_count,
                'deletionsCount': len(read_deletions(10000)),
                'recentDeletions': read_deletions(10),
                'services': services,
            })
            return
        return super().do_GET()

    def _json(self, code: int, payload: dict):
        body = json.dumps(payload).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _delete_doc(self, doc_id: str):
        if not safe_doc_id(doc_id):
            self._json(400, {'ok': False, 'error': 'invalid doc id'})
            return

        target = (DOCS_DIR / doc_id).resolve()
        if DOCS_DIR not in target.parents or not target.exists():
            self._json(404, {'ok': False, 'error': 'document not found'})
            return

        import shutil
        shutil.rmtree(target)
        subprocess.run(['python3', str(REBUILD)], check=False)

        DELETE_LOG.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            'docId': doc_id,
            'deletedAt': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
            'client': self.client_address[0],
            'path': self.path,
        }
        with DELETE_LOG.open('a', encoding='utf-8') as f:
            f.write(json.dumps(entry) + '\n')

        self._json(200, {'ok': True, 'docId': doc_id})

    def do_POST(self):
        m = re.fullmatch(r'/api/docs/([^/]+)/delete', self.path)
        if m:
            self._delete_doc(m.group(1))
            return
        self._json(404, {'ok': False, 'error': 'not found'})

    def do_DELETE(self):
        m = re.fullmatch(r'/api/docs/([^/]+)', self.path)
        if m:
            self._delete_doc(m.group(1))
            return
        self._json(404, {'ok': False, 'error': 'not found'})


if __name__ == '__main__':
    port = int(os.getenv('PDF_LIBRARY_PORT', '8088'))
    server = ThreadingHTTPServer(('0.0.0.0', port), Handler)
    print(f'PDF library server listening on :{port}')
    server.serve_forever()
