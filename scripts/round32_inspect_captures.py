#!/usr/bin/env python3
"""Optional reinspection of preserved private bodies; no network and no overwrite."""
import hashlib
import json
from pathlib import Path
import re
from round31_extract import unique_between, digit_runs
from round32_archive import decode_body, unwrap_archive, verify_capture_identity, visible_text

ROOT = Path(__file__).resolve().parents[1]


def digest(text):
    return hashlib.sha256(text.encode()).hexdigest()


def inspect():
    rows = json.loads((ROOT / 'data/round32_http.json').read_text())
    bodies = {}
    for row in rows:
        raw = (ROOT / row['body_local_ignored']).read_bytes()
        if hashlib.sha256(raw).hexdigest() != row['sha256']:
            raise ValueError('Body mismatch: ' + row['id'])
        html, encoding = decode_body(raw, row['content_type'])
        bodies[row['id']] = (row, html, visible_text(html), encoding)

    primary = {}
    for name in ['bdt_20180504', 'bdt_20190722', 'tibiaevents_20160401', 'tibiaevents_20190302']:
        row, html, text, encoding = bodies[name]
        expected = unwrap_archive(row['requested_url'])
        if len(expected['capture_chain']) != 1:
            raise ValueError('Expected a direct snapshot')
        verify_capture_identity(row, expected['original_url'], expected['capture_chain'][0])
        if name.startswith('bdt_'):
            span = unique_between(text, 'two-eyed', 'BDT: Last')
            if span.count('KNIGHTMARE:') != 1:
                raise ValueError('Answer speaker missing/ambiguous')
            answer = span.split('KNIGHTMARE:', 1)[1].strip()
            obvious = unique_between(text, 'Who knows,', 'BDT: It’s')
        else:
            answer = unique_between(text, 'solve it?).', '- What means')
            obvious = None
        primary[name] = {
            'capture_timestamp': expected['capture_chain'][0],
            'original_url': expected['original_url'],
            'memento_matches': True,
            'answer_sha256': digest(answer),
            'answer_characters': len(answer),
            'answer_digit_runs': digit_runs(answer),
            'obvious_context_sha256': digest(obvious) if obvious is not None else None
        }
    scans = []
    for name in list(primary) + ['rookie_2016_archive', 'tibiabr_2010', 'tibianews_2004_archive', 'tibianews_unscripted_archive']:
        row, html, text, encoding = bodies[name]
        hits = re.findall(r'\bdictionar\w*|\bdicion\w*|wörterbuch', text, re.I)
        scans.append({'source': name, 'encoding': encoding, 'visible_text_sha256': digest(text),
                      'visible_text_characters': len(text), 'literal_dictionary_term_matches': hits})
    notice = bodies['bdt_notice'][1]
    original = 'https://bomdiatibia.com/forum/entrevistas/membros-da-cipsoft-knightmare-o-mito-por-tras-das-historias-tibianas/'
    if original not in notice:
        raise ValueError('Publisher notice no longer contains interview link')
    if 'https://tibiaevents.com/knightmare' not in bodies['secrets_colossus'][1]:
        raise ValueError('Historical interview link not in referral article')
    return {
        'primary_exchanges': primary, 'literal_term_scans': scans,
        'literal_scan_scope': 'Visible page text, not a semantic/synonym search or exhaustive archive review.',
        'bdt_notice_interview_href_verified': True,
        'secrets_tibiaevents_href_verified': True
    }


if __name__ == '__main__':
    expected = json.loads((ROOT / 'data/round32_capture_inspection.json').read_text())
    if inspect() != expected:
        raise ValueError('Preserved capture inspection differs')
    print('Four archived exchanges, Memento identity, referral links and eight literal-term scans reproduced.')
