#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import subprocess
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import unquote

ROOT = Path('/home/ubuntu/.openclaw/workspace/pdf-pipeline/storage').resolve()
DOCS_DIR = (ROOT / 'docs').resolve()
REBUILD = Path('/home/ubuntu/.openclaw/workspace/pdf-pipeline/scripts/rebuild_index.py').resolve()
PREFIX = '/pdf-pipeline/storage'


def safe_doc_id(doc_id: str) -> bool:
    return bool(re.fullmatch(r'[a-zA-Z0-9._-]+', doc_id))


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
