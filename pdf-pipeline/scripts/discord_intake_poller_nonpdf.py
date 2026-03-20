#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import time
from pathlib import Path
from urllib.request import Request, urlopen

STATE_FILE = Path('/home/ubuntu/.openclaw/workspace/pdf-pipeline/.discord-intake-nonpdf-state.json')
INCOMING = Path('/home/ubuntu/.openclaw/workspace/pdf-pipeline/nonpdf/incoming')

TOKEN = os.getenv('DISCORD_BOT_TOKEN', '').strip()
CHANNEL_ID = os.getenv('INTAKE_NONPDF_CHANNEL_ID', '').strip()
POLL_SECONDS = int(os.getenv('INTAKE_NONPDF_POLL_SECONDS', '20'))
DELETE_SOURCE_MESSAGE = os.getenv('DELETE_NONPDF_SOURCE_MESSAGE', 'false').lower() in {'1','true','yes','on'}

API_BASE = 'https://discord.com/api/v10'


def api_get(path: str):
    req = Request(API_BASE + path, headers={
        'Authorization': f'Bot {TOKEN}',
        'User-Agent': 'openclaw-nonpdf-intake/1.0',
    })
    with urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode('utf-8'))


def api_delete(path: str) -> bool:
    req = Request(API_BASE + path, method='DELETE', headers={
        'Authorization': f'Bot {TOKEN}',
        'User-Agent': 'openclaw-nonpdf-intake/1.0',
    })
    try:
        with urlopen(req, timeout=30):
            return True
    except Exception:
        return False


def download(url: str, dst: Path):
    req = Request(url, headers={'User-Agent': 'openclaw-nonpdf-intake/1.0'})
    with urlopen(req, timeout=60) as r:
        dst.write_bytes(r.read())


def load_state():
    if not STATE_FILE.exists():
        return {'seen': []}
    try:
        return json.loads(STATE_FILE.read_text(encoding='utf-8'))
    except Exception:
        return {'seen': []}


def save_state(st):
    STATE_FILE.write_text(json.dumps(st, indent=2), encoding='utf-8')


def safe_name(name: str) -> str:
    keep = "-_.() abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    out = ''.join(c if c in keep else '_' for c in name)
    return out.strip() or 'file.bin'


def run_once():
    st = load_state(); seen = set(st.get('seen', []))
    msgs = api_get(f'/channels/{CHANNEL_ID}/messages?limit=50')
    if not isinstance(msgs, list):
        return
    for m in reversed(msgs):
        mid = m.get('id')
        downloaded_any = False
        for a in (m.get('attachments') or []):
            fn = a.get('filename','')
            aid = a.get('id','')
            if fn.lower().endswith('.pdf'):
                continue
            key = f"{mid}:{aid}:{fn}"
            if key in seen:
                continue
            INCOMING.mkdir(parents=True, exist_ok=True)
            dst = INCOMING / safe_name(f"{mid}-{fn}")
            download(a.get('url',''), dst)
            seen.add(key)
            downloaded_any = True
            print(f"Downloaded non-PDF -> {dst}")
        if downloaded_any and DELETE_SOURCE_MESSAGE and mid:
            ok = api_delete(f'/channels/{CHANNEL_ID}/messages/{mid}')
            print(f"Delete source message {mid}: {'ok' if ok else 'failed'}")

    st['seen'] = list(seen)[-5000:]
    save_state(st)


def main():
    if not TOKEN or not CHANNEL_ID:
        raise SystemExit('DISCORD_BOT_TOKEN and INTAKE_NONPDF_CHANNEL_ID are required')
    while True:
        try:
            run_once()
        except Exception as e:
            print('poll error:', e)
        time.sleep(max(POLL_SECONDS, 5))


if __name__ == '__main__':
    main()
