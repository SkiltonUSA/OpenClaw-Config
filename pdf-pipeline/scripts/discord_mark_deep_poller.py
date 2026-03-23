#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path
from urllib.request import Request, urlopen

STATE_FILE = Path('/home/ubuntu/.openclaw/workspace/pdf-pipeline/.mark-deep-state.json')
RUNNER = Path('/home/ubuntu/.openclaw/workspace/tools/local-deep-researcher/run_and_store.py')

TOKEN = os.getenv('DISCORD_BOT_TOKEN', '').strip()
CHANNEL_ID = os.getenv('MARK_DEEP_CHANNEL_ID', '').strip()
POLL_SECONDS = int(os.getenv('MARK_DEEP_POLL_SECONDS', '10'))
BASE_URL = os.getenv('MARK_DEEP_BASE_URL', 'http://127.0.0.1:8088/pdf-pipeline/storage').rstrip('/')

API_BASE = 'https://discord.com/api/v10'


def api_get(path: str):
    req = Request(API_BASE + path, headers={
        'Authorization': f'Bot {TOKEN}',
        'User-Agent': 'openclaw-mark-deep/1.0',
    })
    with urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode('utf-8'))


def api_post(path: str, payload: dict):
    data = json.dumps(payload).encode('utf-8')
    req = Request(API_BASE + path, method='POST', data=data, headers={
        'Authorization': f'Bot {TOKEN}',
        'User-Agent': 'openclaw-mark-deep/1.0',
        'Content-Type': 'application/json',
    })
    with urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode('utf-8'))


def load_state():
    if not STATE_FILE.exists():
        return {'seen': []}
    try:
        return json.loads(STATE_FILE.read_text(encoding='utf-8'))
    except Exception:
        return {'seen': []}


def save_state(st):
    STATE_FILE.write_text(json.dumps(st, indent=2), encoding='utf-8')


def run_deep(topic: str):
    cmd = ['python3', str(RUNNER), '--topic', topic, '--source-channel', CHANNEL_ID]
    env = os.environ.copy()
    env['PYTHONPATH'] = '/home/ubuntu/.openclaw/workspace/tools/local-deep-researcher/src'
    p = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=1200)
    if p.returncode != 0:
        return {'ok': False, 'error': (p.stderr or p.stdout)[-1000:]}
    try:
        return json.loads(p.stdout)
    except Exception:
        return {'ok': False, 'error': 'Failed to parse runner output'}


def run_once():
    st = load_state(); seen = set(st.get('seen', []))
    msgs = api_get(f'/channels/{CHANNEL_ID}/messages?limit=25')
    if not isinstance(msgs, list):
        return

    for m in reversed(msgs):
        mid = m.get('id')
        if not mid or mid in seen:
            continue
        author = m.get('author', {})
        if author.get('bot'):
            seen.add(mid)
            continue
        content = (m.get('content') or '').strip()
        if not (content.startswith('!deep ') or content.startswith('!research ')):
            seen.add(mid)
            continue

        topic = content.split(' ', 1)[1].strip() if ' ' in content else ''
        if not topic:
            api_post(f'/channels/{CHANNEL_ID}/messages', {'content': 'Usage: `!deep <research topic>`'})
            seen.add(mid)
            continue

        api_post(f'/channels/{CHANNEL_ID}/messages', {'content': f'🧠 Starting deep research on: **{topic}**'})
        result = run_deep(topic)
        if result.get('ok'):
            doc_id = result.get('docId', 'unknown')
            api_post(f'/channels/{CHANNEL_ID}/messages', {
                'content': f'✅ Deep research complete for **{topic}**\nDOC:{doc_id}\nLibrary: <{BASE_URL}/index.html>\nDoc: <{BASE_URL}/docs/{doc_id}/>'
            })
        else:
            api_post(f'/channels/{CHANNEL_ID}/messages', {'content': f'❌ Deep research failed: `{result.get("error", "unknown")[:400]}`'})

        seen.add(mid)

    st['seen'] = list(seen)[-5000:]
    save_state(st)


def main():
    if not TOKEN or not CHANNEL_ID:
        raise SystemExit('DISCORD_BOT_TOKEN and MARK_DEEP_CHANNEL_ID are required')
    while True:
        try:
            run_once()
        except Exception as e:
            print('poll error:', e)
        time.sleep(max(POLL_SECONDS, 5))


if __name__ == '__main__':
    main()
