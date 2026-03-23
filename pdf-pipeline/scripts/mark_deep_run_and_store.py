#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

# local-deep-researcher package path (cloned repo)
if '/home/ubuntu/.openclaw/workspace/tools/local-deep-researcher/src' not in os.sys.path:
    os.sys.path.insert(0, '/home/ubuntu/.openclaw/workspace/tools/local-deep-researcher/src')

from ollama_deep_researcher.graph import graph  # type: ignore

ROOT = Path('/home/ubuntu/.openclaw/workspace')
STORE = ROOT / 'pdf-pipeline' / 'storage' / 'docs'
REBUILD = ROOT / 'pdf-pipeline' / 'scripts' / 'rebuild_index.py'


def slugify(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r'[^a-z0-9]+', '-', s)
    return s.strip('-') or 'research'


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--topic', required=True)
    ap.add_argument('--loops', type=int, default=2)
    ap.add_argument('--uploaded-by', default='discord:mark')
    ap.add_argument('--source-channel', default='')
    ap.add_argument('--doc-id', default='')
    args = ap.parse_args()

    doc_id = args.doc_id or f"{datetime.now(timezone.utc).strftime('%Y-%m-%d')}-{slugify(args.topic)[:70]}"
    doc_dir = STORE / doc_id
    doc_dir.mkdir(parents=True, exist_ok=True)

    cfg = {
        'configurable': {
            'llm_provider': 'ollama',
            'local_llm': 'llama3.2:3b',
            'search_api': 'duckduckgo',
            'max_web_research_loops': args.loops,
            'fetch_full_page': True,
            'use_tool_calling': False,
            'strip_thinking_tokens': True,
            'ollama_base_url': 'http://127.0.0.1:11434',
        }
    }

    result = graph.invoke({'research_topic': args.topic}, config=cfg)
    summary = (result or {}).get('running_summary') or 'No summary generated.'

    (doc_dir / 'parsed.md').write_text(summary, encoding='utf-8')
    (doc_dir / 'parsed.json').write_text(json.dumps({'topic': args.topic, 'result': result}, indent=2), encoding='utf-8')
    (doc_dir / 'summary.md').write_text(summary[:4000], encoding='utf-8')

    manifest = {
        'docId': doc_id,
        'title': f'Deep Research: {args.topic}',
        'uploadedAt': utc_now(),
        'uploadedBy': args.uploaded_by,
        'sourceChannel': args.source_channel,
        'tags': ['deep-research', 'mark'],
        'files': {
            'original': None,
            'markdown': 'parsed.md',
            'json': 'parsed.json',
            'summary': 'summary.md',
        },
        'parser': {
            'name': 'local-deep-researcher',
            'mode': 'ollama-local',
            'version': 'repo-local',
            'status': 'ok',
            'notes': f'loops={args.loops}, model=llama3.2:3b, search=duckduckgo',
        }
    }
    (doc_dir / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')

    subprocess.run(['python3', str(REBUILD)], check=False)

    print(json.dumps({'ok': True, 'docId': doc_id, 'docDir': str(doc_dir)}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
