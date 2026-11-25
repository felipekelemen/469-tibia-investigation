#!/usr/bin/env python3
"""Optional replay against private captured HTML; public offline audit is separate.

Boundary selection was made after inspecting the pages. These hashes preserve
that inspection; they are not a preregistered semantic classifier.
"""
import hashlib
import json
from pathlib import Path
import re
from round31_extract import paragraphs, unique_between, unique_exchange, digit_runs

ROOT = Path(__file__).resolve().parents[1]


def digest(text):
    return hashlib.sha256(text.encode()).hexdigest()


def inspect():
    metadata = json.loads((ROOT / 'data/round31_http.json').read_text())
    out = {'teyrata': [], 'knightmare': {}, 'chayenne': {}}
    for row in metadata:
        path = ROOT / row['body_local_ignored']
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != row['sha256']:
            raise ValueError('Captured body mismatch: ' + row['id'])
        if row['id'] not in {'teyrata_portal', 'teyrata_wiki', 'teyrata_oldid',
                              'knightmare_portal_2014', 'chayenne_2009'}:
            continue
        if row['http_status'] != 200 or row['human_check_marker'] or row['body_truncated']:
            raise ValueError('Incomplete or challenge page')
        html = raw.decode('utf-8')
        blocks = paragraphs(html)
        text = ' '.join(blocks)
        if row['id'].startswith('teyrata_'):
            answer = unique_between(text, 'numbers?', 'Joey')
            if not answer.startswith('Teyrata:'):
                raise ValueError('Speaker mismatch')
            reply = answer.split(':', 1)[1].strip()
            # Page versions use either an ASCII smile or its emoji equivalent.
            lexical = re.sub(r'\s*(?::\)|🙂)$', '', reply)
            revision = re.search(r'"wgRevisionId":([0-9]+)', html)
            out['teyrata'].append({'source': row['id'],
                'revision_id': int(revision[1]) if revision else None,
                'answer_sha256': digest(answer), 'answer_digit_runs': digit_runs(reply),
                'lexical_reply_sha256': digest(lexical)})
        elif row['id'] == 'knightmare_portal_2014':
            frame = unique_exchange(blocks, 'linguagem Bonelord?', 'Knightmare:')
            out['knightmare'] = {'question_index': frame['question_index'],
                'answer_index': frame['answer_index'],
                'question_sha256': digest(frame['question']),
                'answer_sha256': digest(frame['answer']),
                'answer_digit_runs': digit_runs(frame['answer'])}
        elif row['id'] == 'chayenne_2009':
            inventory = json.loads((ROOT / 'data/source_validation_inventory.json').read_text())
            rows = [r for r in inventory if r['source_group'] == 'chayenne_interview']
            out['chayenne'] = {r['id']: {'digits': r['text'],
                'raw_html_occurrences': html.count(r['text'])} for r in rows}
    return out


if __name__ == '__main__':
    actual = inspect()
    expected = json.loads((ROOT / 'data/round31_capture_inspection.json').read_text())
    if actual != expected:
        raise ValueError('Inspection changed')
    print('Private HTML hashes, answer boundaries and numeric runs reproduced.')
