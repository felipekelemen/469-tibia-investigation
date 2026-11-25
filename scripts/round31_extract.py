#!/usr/bin/env python3
"""Extract HTML paragraph boundaries without joining separate interview answers.

This is a document utility, not an automatic attribution/meaning classifier.
"""
from html.parser import HTMLParser
import re


def normalized(text):
    return ' '.join(text.split())


class Paragraphs(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks = []
        self.parts = None
        self.hidden = 0

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'):
            self.hidden += 1
        if self.hidden:
            return
        if tag == 'p':
            self.finish()
            self.parts = []
        elif tag == 'br' and self.parts is not None:
            self.parts.append(' ')
        elif tag == 'img' and self.parts is not None:
            self.parts.append(dict(attrs).get('alt', ''))

    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self.hidden = max(0, self.hidden - 1)
        if tag == 'p' and not self.hidden:
            self.finish()

    def handle_data(self, data):
        if self.parts is not None and not self.hidden:
            self.parts.append(data)

    def finish(self):
        if self.parts is not None:
            value = normalized(''.join(self.parts))
            if value:
                self.blocks.append(value)
            self.parts = None


def paragraphs(html):
    parser = Paragraphs()
    parser.feed(html)
    parser.finish()
    return parser.blocks


def unique_exchange(blocks, question_anchor, answer_prefix):
    """Require exactly one question and its immediate following paragraph.

    Ambiguous, translated duplicate or merged-block pages fail closed; inspect
    them manually instead of silently choosing a convenient occurrence.
    """
    positions = [i for i, b in enumerate(blocks) if question_anchor in b]
    if len(positions) != 1:
        raise ValueError('Question anchor missing or ambiguous')
    i = positions[0]
    if i + 1 >= len(blocks) or not blocks[i + 1].startswith(answer_prefix):
        raise ValueError('Immediate answer boundary not established')
    return {'question_index': i, 'answer_index': i + 1,
            'question': blocks[i], 'answer': blocks[i + 1]}


def digit_runs(text):
    # Keep groups intact; never strip every non-digit in an entire web page.
    return re.findall(r'[0-9]+', text)


def unique_between(text, start, end):
    """Exact, pre-inspected delimiters for pages merging multiple Q/A in a p.

    Do not infer where an answer ends from its apparent meaning or numbers.
    """
    if text.count(start) != 1 or text.count(end) != 1:
        raise ValueError('Delimiters missing or ambiguous')
    a = text.index(start) + len(start)
    b = text.index(end)
    if b <= a:
        raise ValueError('Reversed or overlapping delimiters')
    return text[a:b].strip()
