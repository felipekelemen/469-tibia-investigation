#!/usr/bin/env python3
"""Nonmutating replay of numeric photo projections and corpus copy seams."""
import photo_conversion_audit as photo
import source_copy_seams as seams


def verify_available_captures():
    checked = 0
    manifest = photo.load('data/round19_http_manifest.json')
    byid = {row['id']: row for row in manifest}
    for row in manifest:
        path = photo.ROOT / row['body_local_ignored']
        if path.exists():
            if photo.sha(row['body_local_ignored']) != row['sha256']:
                raise ValueError('captured source changed: ' + row['id'])
            checked += 1
    extracted = []
    raw = photo.ROOT / byid['conversion_raw']['body_local_ignored']
    html = photo.ROOT / byid['conversion_html']['body_local_ignored']
    if raw.exists():
        extracted.append(photo.numeric_rows(raw.read_text(encoding='utf-8-sig')))
    if html.exists():
        parser = photo.CodeLines()
        parser.feed(html.read_text())
        extracted.append(photo.numeric_rows('\n'.join(parser.lines)))
    expected = photo.load('data/round19_conversion_numeric.json')['rows']
    for rows in extracted:
        if [r[1:] for r in rows] != [r[1:] for r in expected]:
            raise ValueError('source extraction changed')
    print(f'Source bodies locally rehashed: {checked}/{len(manifest)}. '
          'Missing bodies are not reauthenticated by the offline replay.')


def main():
    photo.main(check=True)
    verify_available_captures()
    for path, expected in seams.load('data/round19_copy_boundary_manifest.json')['sha256'].items():
        if seams.sha(path) != expected:
            raise ValueError('copy-seam input changed: ' + path)
    result = seams.build()
    if result != seams.load('results/round19_copy_seams.json'):
        raise ValueError('copy-seam replay mismatch')
    print('Six projections fail calibration; photo null comparisons are NOT APPLICABLE. '
          'All copy cuts and 2,997 copy controls replayed. No English translation.')


if __name__ == '__main__':
    main()
