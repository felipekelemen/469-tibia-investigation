import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from round32_archive import decode_body, unwrap_archive, verify_capture_identity, visible_text


class ArchiveIdentityTests(unittest.TestCase):
    def test_nested_rewrite_preserves_inner_snapshot(self):
        value=unwrap_archive('https://web.archive.org/web/20230107101212/https://web.archive.org/web/20180504032226/https://example.com/interview?q=7#post2')
        self.assertEqual(value, {'original_url':'https://example.com/interview?q=7#post2', 'capture_chain':['20230107101212','20180504032226']})

    def test_raw_replay_modifier(self):
        self.assertEqual(unwrap_archive('https://web.archive.org/web/20180504032226id_/http://example.com/a')['original_url'], 'http://example.com/a')

    def test_nonarchive_domain_is_not_rewritten(self):
        url='https://example.com/web/20180504032226/https://elsewhere.org/'
        self.assertEqual(unwrap_archive(url), {'original_url':url,'capture_chain':[]})

    def test_incomplete_or_impossible_timestamp_rejected(self):
        for url in ['https://web.archive.org/web/2018/https://example.com', 'https://web.archive.org/web/20181304032226/https://example.com']:
            with self.assertRaises(ValueError):unwrap_archive(url)

    def row(self):
        return {'http_status':200,'body_truncated':False,'human_check_marker':False,
                'final_url_without_query':'https://web.archive.org/web/20180504032226/https://example.com/a',
                'memento_datetime':'Fri, 04 May 2018 03:22:26 GMT'}

    def test_valid_capture_identity(self):
        self.assertTrue(verify_capture_identity(self.row(),'https://example.com/a','20180504032226'))

    def test_availability_claim_cannot_override_body_failure(self):
        row=self.row();row['http_status']=404
        with self.assertRaises(ValueError):verify_capture_identity(row,'https://example.com/a','20180504032226')
        for field in ['body_truncated','human_check_marker']:
            row=self.row();row[field]=True
            with self.assertRaises(ValueError):verify_capture_identity(row,'https://example.com/a','20180504032226')

    def test_silent_redirect_to_different_date_rejected(self):
        row=self.row();row['memento_datetime']='Sat, 05 May 2018 03:22:26 GMT'
        with self.assertRaises(ValueError):verify_capture_identity(row,'https://example.com/a','20180504032226')

    def test_visible_text_handles_inline_entities_and_hidden_decoys(self):
        self.assertEqual(visible_text('<div>trans<span>lator</span>&nbsp;&amp; eyes<script>dictionary 3478</script></div><p>next</p>'), 'translator & eyes next')

    def test_declared_legacy_encoding_preserved(self):
        text,encoding=decode_body(b'dicion\xe1rio', 'text/html; charset=ISO-8859-1')
        self.assertEqual(text,'dicionário')
        self.assertEqual(encoding,'ISO-8859-1')
        with self.assertRaises(UnicodeDecodeError):decode_body(b'\xe1','text/html; charset=UTF-8')


if __name__ == '__main__':unittest.main()
