#!/usr/bin/env python3
"""Read retained public captures without promoting publication dates to captures.

Original page bodies are local/ignored. This helper returns a selected comment;
the public evidence ledger retains only factual dates and numeric matrices.
"""
import html
import json
from html.parser import HTMLParser


class SourceHTML(HTMLParser):
    def __init__(self):
        super().__init__()
        self.scripts = []
        self.text = []
        self.images = []
        self.links = []
        self._script = None
        self._skip = 0

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if tag == 'script':
            self._script = [] if attrs.get('type', '').lower() == 'application/ld+json' else None
            self._skip += 1
        if tag == 'style':
            self._skip += 1
        if tag == 'img' and attrs.get('src'):
            self.images.append(attrs['src'])
        if tag == 'a' and attrs.get('href'):
            self.links.append(attrs['href'])

    def handle_endtag(self, tag):
        if tag == 'script':
            if self._script is not None:
                self.scripts.append(json.loads(''.join(self._script)))
            self._script = None
            self._skip = max(0, self._skip - 1)
        if tag == 'style':
            self._skip = max(0, self._skip - 1)

    def handle_data(self, data):
        if self._script is not None:
            self._script.append(data)
        if not self._skip:
            self.text.append(data)


def objects(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from objects(child)
    elif isinstance(value, list):
        for child in value:
            yield from objects(child)


def comment(source, marker, author=None, published_prefix=None):
    parsed = SourceHTML()
    parsed.feed(source)
    matches = []
    for script in parsed.scripts:
        for item in objects(script):
            if item.get('@type') != 'Comment' or marker not in html.unescape(item.get('text', '')):
                continue
            if author is not None and item.get('author', {}).get('name') != author:
                continue
            if published_prefix is not None and not item.get('datePublished', '').startswith(published_prefix):
                continue
            matches.append(item)
    if len(matches) != 1:
        raise ValueError(f'expected one matching comment, found{len(matches)}')
    item = matches[0]
    return {'publication_timestamp_reported': item['datePublished'],
            'author_display_name': item.get('author', {}).get('name'),
            'text_local_only': html.unescape(item['text']),
            'game_capture_timestamp': None,
            'historical_body_archive_timestamp': None,
            'date_semantics': 'Current platform attribution of publication; not an authenticated historical body or game-capture date.'}


def visible_text(source):
    parsed = SourceHTML()
    parsed.feed(source)
    return '\n'.join(parsed.text)
