#!/usr/bin/env python3
"""Post-outcome independent necessary-condition certificates, not another search.

Build rows then columns without importing the inference/encryption code. If
every column mismatches the desired prefix, no column-order permutation works.
"""
import hashlib
import itertools
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]


def prefix_certificate(source, target, config):
    input_view = ''.join(reversed(source)) if config['reverse_input'] else source
    output_view = ''.join(reversed(target)) if config['reverse_output'] else target
    fill, stream = (input_view, output_view) if config['operation'] == 'encrypt' else (output_view, input_view)
    w = config['width']
    grid = [fill[i:i + w] for i in range(0, len(fill), w)]
    witnesses = []
    for column in range(w):
        text = ''.join(row[column] for row in grid if column < len(row))
        if stream.startswith(text):
            return None
        for j, (actual, desired) in enumerate(zip(text, stream)):
            if actual != desired:
                witnesses.append({'column_index': column, 'first_mismatch_in_column': j,
                                  'column_digit': actual, 'required_prefix_digit': desired})
                break
        else:
            raise ValueError('length mismatch outside this certificate contract')
    return {'config': config, 'all_columns_excluded': True, 'witnesses': witnesses}


def certificates(source, target, widths):
    return [prefix_certificate(source, target, {'width': width, 'operation': operation,
                                               'reverse_input': ri, 'reverse_output': ro})
            for width in widths for operation in ('encrypt', 'decrypt')
            for ri, ro in itertools.product((False, True), repeat=2)]


def main():
    p = json.loads((ROOT / 'data/columnar_pair_protocol.json').read_text())
    books = json.loads((ROOT / 'data/normalized_books.json').read_text())
    source = next(b['digits'] for b in books if b['id'] == '22')
    target = json.loads((ROOT / 'data/external_book_round10.json').read_text())['digits']
    rows = certificates(source, target, p['widths'])
    if len(rows) != 248 or any(row is None for row in rows):
        raise ValueError('not every primary parameterization has a prefix certificate')
    out = {'scope': 'Post-outcome independent audit of a necessary condition; no fitting, new family, p-value or semantic inference.',
           'performed_after_primary_outcome': True,
           'protocol_sha256': hashlib.sha256((ROOT / 'data/columnar_pair_protocol.json').read_bytes()).hexdigest(),
           'certificates': rows}
    path = ROOT / 'results/columnar_prefix_certificates.json'
    if path.exists():
        raise RuntimeError('certificate artifact already exists')
    path.write_text(json.dumps(out, indent=2) + '\n')
    print('Independent row-built prefix certificates:', len(rows))


if __name__ == '__main__':
    main()
