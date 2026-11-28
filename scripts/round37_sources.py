#!/usr/bin/env python3
"""Index existing private captures. Does not search, fetch, or authenticate meanings."""
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT/'data/private/round37'


def load(path):
    return json.loads(path.read_text())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def collect_queries(value):
    out = set()
    if isinstance(value, dict):
        for key, child in value.items():
            if key in ['q', 'query'] and isinstance(child, str):
                out.add(child)
            elif key == 'queries' and isinstance(child, list):
                out.update(x for x in child if isinstance(x, str))
            out.update(collect_queries(child))
    elif isinstance(value, list):
        for child in value:
            out.update(collect_queries(child))
    return out


def collect():
    records, queries = [], []
    counts = dict(search=0, open=0, find=0, click=0, direct_http=0)
    for name in ['search01','search02','open01','open02','search03','open03','find01','click01']:
        path = PRIVATE/(name+'.json')
        params = load(path)['params']
        record = {'path_local_ignored': str(path.relative_to(ROOT)), 'sha256': digest(path), 'params': params}
        records.append(record)
        for key in ['system2_search_query', 'open', 'find', 'click']:
            if key not in params:
                continue
            count_key = 'search' if key == 'system2_search_query' else key
            counts[count_key] += len(params[key])
            if count_key == 'search':
                queries.extend(q['q'] for q in params[key])
    http = []
    for name in ['data/round37_http.json','data/round37_http_retry.json','data/round37_http_followup.json']:
        for row in load(ROOT/name):
            assert digest(ROOT/row['body_local_ignored']) == row['sha256']
            http.append(dict(row, capture_manifest=name))
    counts['direct_http'] = len(http)
    prior_paths = [f'data/round{n}_discovery_log.json' for n in [24,26,31,32,34]]
    prior = set()
    for name in prior_paths:
        prior.update(collect_queries(load(ROOT/name)))
    counts['web_open_click_find'] = sum(counts[k] for k in ['open','find','click'])
    return {'round':37, 'retrieval_date_utc':'2026-11-28', 'counts':counts,
            'counting':'Every request including failed and repeated reads; counts are not independent sources.',
            'distinct_queries':len(set(queries)), 'queries':queries,
            'prior_query_inventory':{'paths':prior_paths,'count':len(prior),
                                     'literal_repeats':sorted(set(queries)&prior)},
            'calls':records, 'http':http,
            'new_author_authenticated_anchor':False,
            'closure':'Bounded search ended after 12 queries and targeted provenance checks; not a claim that all public sources are exhausted.'}


def article_extract():
    capture = PRIVATE/'find01.json'
    blocks = [c.get('text','') for c in load(capture)['result']['content']]
    tables = []
    for text in blocks:
        if 'tibiasecrets.com/article160' not in text:
            continue
        rows = {}
        for line in text.splitlines():
            m = re.match(r'L\d+: ([0-9])  \| (.*)$', line)
            if m:
                cells = [c.strip() for c in m.group(2).split('|')]
                assert len(cells) == 10
                rows[m.group(1)] = cells
        if len(rows) == 10:
            tables.append({r+str(i):c for r,cells in rows.items() for i,c in enumerate(cells) if c})
    assert tables and all(t == tables[0] for t in tables)
    claims = load(ROOT/'data/round37_claims.json')['article160']
    relevant = {p:tables[0][p] for p in claims['relevant_pair_map']}
    assert relevant == claims['relevant_pair_map']
    expansions = {}
    for text in blocks:
        if 'tibiasecrets.com/article160' not in text:
            continue
        for line in text.splitlines():
            m = re.fullmatch(r'L\d+: ([A-Z]): ([A-Z, ]+)', line)
            if m:
                expansions[m.group(1)] = m.group(2).split(', ')
    assert {k:expansions[k] for k in claims['expansions'] if k != '*'} == {
        k:v for k,v in claims['expansions'].items() if k != '*'}
    return {'url':claims['url'], 'capture_local_ignored':str(capture.relative_to(ROOT)),
            'capture_sha256':digest(capture), 'access':'Search connector extracted page; direct HTTP returned 403',
            'relevant_pair_map':relevant, 'relevant_expansions':{k:expansions[k] for k in claims['expansions'] if k != '*'},
            'wildcard_operationalization':'Any letter restricted here to uppercase English A..Z; declared assumption, not an authenticated alphabet',
            'table_and_expansions_match_frozen_claims':True}


if __name__ == '__main__':
    for name, result in [('data/round37_discovery_log.json',collect()),
                         ('data/round37_article_extract.json',article_extract())]:
        target = ROOT/name
        assert not target.exists(), 'Preserve existing records'
        target.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    print('Capture index and table extraction verified.')
