#!/usr/bin/env python3
"""Archive identity and visible-text utilities; no semantic classification."""
import datetime
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser
import re
from urllib.parse import urlsplit


class Visible(HTMLParser):
    """Keep inline text contiguous; ignore scripts/styles, separate block tags."""
    BREAKS = {'p', 'div', 'br', 'li', 'tr', 'td', 'th', 'h1', 'h2', 'h3', 'h4', 'blockquote'}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.hidden = 0

    def handle_starttag(self, tag, attrs):
        if tag in {'script', 'style'}:
            self.hidden += 1
        if not self.hidden and tag in self.BREAKS:
            self.parts.append(' ')

    def handle_endtag(self, tag):
        if tag in {'script', 'style'}:
            self.hidden = max(0, self.hidden - 1)
        if not self.hidden and tag in self.BREAKS:
            self.parts.append(' ')

    def handle_data(self, data):
        if not self.hidden:
            self.parts.append(data)


def visible_text(html):
    parser = Visible()
    parser.feed(html)
    return ' '.join(''.join(parser.parts).split())


def decode_body(raw, content_type):
    match = re.search(r'charset\s*=\s*["\']?([\w-]+)', content_type, re.I)
    encoding = match[1] if match else 'utf-8'
    return raw.decode(encoding), encoding


def unwrap_archive(url):
    """Unwrap up to eight Wayback rewrite layers, preserving timestamps and URL.

    A rewritten historical link can nest an archive address. The outer wrapper
    is not the capture date of the inner linked page. Do not strip its query.
    """
    chain = []
    for _ in range(8):
        parsed = urlsplit(url)
        if parsed.hostname not in {'web.archive.org', 'www.web.archive.org'}:
            return {'original_url': url, 'capture_chain': chain}
        match = re.match(r'^/web/(\d{14})(?:[a-z]+_)?/(https?://.*)$', parsed.path)
        if not match:
            raise ValueError('Unsupported or incomplete archive URL')
        stamp, original = match.groups()
        datetime.datetime.strptime(stamp, '%Y%m%d%H%M%S')
        if parsed.query:
            original += '?' + parsed.query
        if parsed.fragment:
            original += '#' + parsed.fragment
        chain.append(stamp)
        url = original
    raise ValueError('Too many nested archive wrappers')


def verify_capture_identity(row, expected_original, expected_stamp):
    """A valid archived HTTP response is still not proof it contains an interview."""
    if row.get('http_status') != 200 or row.get('body_truncated') or row.get('human_check_marker'):
        raise ValueError('Response is not a complete unchallenged HTTP200 capture')
    final = unwrap_archive(row['final_url_without_query'])
    if final['capture_chain'] != [expected_stamp] or final['original_url'] != expected_original:
        raise ValueError('Archive timestamp/original URL differs')
    memento = parsedate_to_datetime(row['memento_datetime'])
    if memento.tzinfo is None:
        raise ValueError('Memento datetime has no timezone')
    if memento.astimezone(datetime.timezone.utc).strftime('%Y%m%d%H%M%S') != expected_stamp:
        raise ValueError('Memento header disagrees with archive timestamp')
    return True
