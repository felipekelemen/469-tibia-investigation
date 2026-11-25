import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from round31_extract import paragraphs, unique_exchange, unique_between, digit_runs


class InterviewExtractionTests(unittest.TestCase):
    def test_hidden_digits_and_inline_words(self):
        html = '<p>A: l<strong>an</strong>guage &amp; script<script>3478</script></p>'
        self.assertEqual(paragraphs(html), ['A: language & script'])

    def test_other_answers_and_page_dates_do_not_leak(self):
        blocks = paragraphs('<p>2026</p><p>Q: numbers?</p><p>A: none.</p>'
                            '<p>Q: year?</p><p>A: 2014.</p>')
        exchange = unique_exchange(blocks, 'numbers?', 'A:')
        self.assertEqual(digit_runs(exchange['answer']), [])

    def test_merged_questions_require_explicit_boundaries(self):
        blocks = paragraphs('<p>Q: numbers? A: none. Next: 2014</p>')
        with self.assertRaises(ValueError):
            unique_exchange(blocks, 'numbers?', 'A:')
        self.assertEqual(unique_between(blocks[0], 'numbers?', 'Next:'), 'A: none.')

    def test_duplicate_source_repetition_is_not_silently_chosen(self):
        with self.assertRaises(ValueError):
            unique_exchange(['Q: cipher?', 'A: 3478', 'Q: cipher?', 'A: 3478'], 'cipher?', 'A:')
        with self.assertRaises(ValueError):
            unique_between('start X end start X end', 'start', 'end')

    def test_reversed_and_missing_boundaries(self):
        for text in ['end start', 'start only']:
            with self.assertRaises(ValueError):
                unique_between(text, 'start', 'end')

    def test_preserves_digit_grouping_and_zero(self):
        self.assertEqual(digit_runs('0007 :) 0 xD 123!'), ['0007', '0', '123'])

    def test_no_meaning_answer_stays_with_its_question(self):
        blocks = ['Q: name?', 'A: no meaning', 'Q: numbers?', 'A: 0007']
        self.assertEqual(unique_exchange(blocks, 'numbers?', 'A:')['answer'], 'A: 0007')


if __name__ == '__main__':
    unittest.main()
