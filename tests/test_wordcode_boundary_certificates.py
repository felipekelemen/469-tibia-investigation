import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from wordcode_boundary_certificates import build


class BoundaryCertificateTests(unittest.TestCase):
    def test_other_standalone_pairing_is_possible_without_book_context(self):
        data = build()
        targets = {r['target_id']: r['target'] for r in data['records']}
        for row in data['standalone_pair_counterexamples']:
            self.assertEqual(''.join(row['fixed_pairs']), targets[row['target_id']])
            self.assertTrue(row['all_codes_in_imported_inventory'])

    def test_every_certified_span_replays_from_full_book_emissions(self):
        books = {b['id']: b for b in json.loads((ROOT / 'data/normalized_books.json').read_text())}
        rows = build()['records']
        seen = set()
        for row in rows:
            b = books[row['book_id']]
            mask = set(row['source_omitted_indices'])
            wires = [code[1:] if i in mask else code for i, code in enumerate(b['codes'])]
            self.assertEqual(''.join(wires), b['digits'])
            starts = [sum(map(len, wires[:i])) for i in range(len(wires)+1)]
            self.assertEqual(row['start_is_code_boundary'], row['raw_start'] in starts)
            self.assertEqual(row['end_is_code_boundary'], row['raw_end'] in starts)
            self.assertEqual(b['digits'][row['raw_start']:row['raw_end']], row['target'])
            parent = ''.join(e['wire'] for e in row['parent_emissions'])
            self.assertEqual(parent, row['left_book_remainder']+row['target']+row['right_book_remainder'])
            for emission in row['parent_emissions']:
                i = emission['index']
                self.assertEqual(emission['code'], b['codes'][i])
                self.assertEqual((emission['start'], emission['end']), (starts[i], starts[i+1]))
            seen.add((row['target_id'], row['book_id'], row['raw_start']))
        self.assertEqual(len(seen), 7)


if __name__ == '__main__':
    unittest.main()
