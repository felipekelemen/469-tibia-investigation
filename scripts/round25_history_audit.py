#!/usr/bin/env python3
"""Extract revision facts from local captures; do not date a game update from a wiki edit."""
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def audit():
    rows = []
    for path in sorted(ROOT.glob('data/round25_history_http_*.json')):
        for capture in json.loads(path.read_text()):
            raw = (ROOT/capture['body_local_ignored']).read_bytes()
            assert hashlib.sha256(raw).hexdigest() == capture['sha256']
            payload = json.loads(raw)
            for page in payload.get('query',{}).get('pages',[]):
                for rev in page.get('revisions',[]):
                    content = rev.get('slots',{}).get('main',{}).get('content','')
                    if not content:
                        continue
                    assert hashlib.sha1(content.encode()).hexdigest() == rev['sha1']
                    name = re.search(r'(?mi)^\s*\|\s*name\s*=\s*(.*)',content)
                    rows.append({'revid':rev['revid'], 'parentid':rev['parentid'], 'wiki_revision_timestamp':rev['timestamp'],
                                 'content_sha1_verified':rev['sha1'], 'name_parameter':name.group(1).strip() if name else None,
                                 'contains_3478': '3478' in content,
                                 'mentions_2023': '2023' in content,
                                 'source_url':'https://www.tibiawiki.com.br/index.php?oldid='+str(rev['revid']),
                                 'capture_sha256':capture['sha256']})
    rows.sort(key=lambda r:r['revid'])
    return {'revisions':rows, 'scope':'Current MediaWiki API supplies dated revision content and matching SHA1. This authenticates the retrieved wiki record, not a signed CipSoft release or actual game-change date.',
            'game_event_date_proven':False, 'internal_entity_id_proven':False, 'translation_proven':False}


if __name__ == '__main__':
    (ROOT/'results/round25_history.json').write_text(json.dumps(audit(),indent=2)+'\n')
