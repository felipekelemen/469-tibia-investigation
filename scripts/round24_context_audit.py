#!/usr/bin/env python3
"""Optional replay against ignored original HTTP bodies (never a translation)."""
from html.parser import HTMLParser
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


class VisibleText(HTMLParser):
    def __init__(self):
        super().__init__(); self.hidden = 0; self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'):
            self.hidden += 1

    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self.hidden = max(0, self.hidden - 1)

    def handle_data(self, value):
        if not self.hidden:
            self.parts.append(value)


def visible(body):
    parser = VisibleText(); parser.feed(body)
    return ' '.join(' '.join(parser.parts).split())


def group_matches(text, target):
    groups, wanted = re.findall(r'\d+', text), re.findall(r'\d+', target)
    return sum(groups[i:i + len(wanted)] == wanted for i in range(len(groups) - len(wanted) + 1))


def run():
    captures = {r['id']: r for p in sorted(ROOT.glob('data/round24_http_*.json'))
                if 'targets' not in p.name for r in json.loads(p.read_text())}
    inventory = {r['id']: r['text'] for r in json.loads((ROOT/'data/source_validation_inventory.json').read_text())}
    targets = {'chayenne_2009': ['chayenne_2009_part1', 'chayenne_2009_part2'],
               'avar_secrets': ['avar_tar_poem'], 'wiki469': ['knightmare_2012'],
               'knight_wiki': ['knightmare_2012']}
    results = {}
    for source, names in targets.items():
        row = captures[source]; raw = (ROOT/row['body_local_ignored']).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == row['sha256']
        text = visible(raw.decode('utf-8', errors='replace'))
        results[source] = {'body_sha256': row['sha256'], 'target_numeric_group_occurrences':
                           {name: group_matches(text, inventory[name]) for name in names}}
    row = captures['honeminas_correct']; raw = (ROOT/row['body_local_ignored']).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == row['sha256']
    text = visible(raw.decode('utf-8', errors='replace'))
    vectors = re.findall(r'\(\s*4\s*,\s*3\s*,\s*1\s*,\s*5\s*,\s*3\s*\)\s*\.\s*\(\s*3\s*,\s*4\s*,\s*7\s*,\s*8\s*,\s*4\s*\)', text)
    results['honeminas_correct'] = {'body_sha256': row['sha256'], 'correct_vector_pair_occurrences': len(vectors),
                                    'dot_product_under_ordinary_arithmetic': sum(a*b for a,b in zip([4,3,1,5,3],[3,4,7,8,4]))}
    return {'sources': results, 'scope': 'Numeric transcription checks only; body captures local/ignored. Current web copies do not date the original game text.', 'translation_validated': False}


if __name__ == '__main__':
    output = run(); (ROOT/'results/round24_context.json').write_text(json.dumps(output, indent=2)+'\n')
