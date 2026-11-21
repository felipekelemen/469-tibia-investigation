#!/usr/bin/env python3
"""Bounded exact counterexample queries; no consensus from incomplete searches."""
from unit_morphism_solver import key_tuple, word_extensions, word_pattern


class Model:
    def __init__(self, words, bank):
        self.words = list(dict.fromkeys(words))
        self.bank = bank
        self.digits = set(''.join(self.words))
        self.domains = []
        for raw in self.words:
            pattern = word_pattern(raw, bank.minimum, bank.maximum, {})
            forms = (f for n in bank.lengths
                     if len(raw)*bank.minimum <= n <= len(raw)*bank.maximum
                     for f in bank.by_length[n])
            self.domains.append(tuple(f for f in forms if pattern.fullmatch(f)))

    def find(self, different_key=None, different_form=None,
             max_states=2000, local_cap=20000):
        """SAT witness, exhaustive UNSAT, or UNKNOWN. Exclusions are conjunctions.

        different_key: require at least one named assignment to differ.
        different_form: (raw, form), require its emitted string to differ.
        Queries may only reference observed training digits.
        """
        if different_key is not None and not set(different_key) <= self.digits:
            raise ValueError('cannot constrain unseen digits')
        if different_form and not set(different_form[0]) <= self.digits:
            raise ValueError('cannot constrain unseen digits')
        seen = set()
        out = {'status': 'UNSAT', 'key': None, 'states': 0, 'limit': None}
        class Stop(Exception):
            pass

        def limited(reason):
            out.update(status='UNKNOWN', limit=reason)
            raise Stop

        def visit(key, domains):
            kt = key_tuple(key)
            if kt in seen:
                return
            if len(seen) >= max_states:
                limited('states')
            seen.add(kt)
            if different_key is not None and all(d in key for d in different_key):
                if all(key[d] == u for d, u in different_key.items()):
                    return
            if different_form:
                raw, form = different_form
                if all(d in key for d in raw) and emit(raw, key) == form:
                    return
            filtered, choices = [], []
            for i, (raw, fs) in enumerate(zip(self.words, domains)):
                if all(d in key for d in raw):
                    form = emit(raw, key)
                    if form not in fs:
                        return
                    matches = (form,)
                else:
                    pattern = word_pattern(raw, self.bank.minimum, self.bank.maximum, key)
                    matches = tuple(f for f in fs if pattern.fullmatch(f))
                    if not matches:
                        return
                    choices.append((len(matches), i))
                filtered.append(matches)
            if not choices:
                out.update(status='SAT', key=dict(key))
                raise Stop
            _, i = min(choices)
            extensions = set()
            for form in filtered[i]:
                for candidate in word_extensions(self.words[i], form,
                        self.bank.minimum, self.bank.maximum, key):
                    nk = key_tuple(candidate)
                    if nk in extensions:
                        continue
                    if len(extensions) >= local_cap:
                        limited('local_assignments')
                    extensions.add(nk)
                    visit(candidate, filtered)
        try:
            visit({}, self.domains)
        except Stop:
            pass
        out['states'] = len(seen)
        return out


def emit(raw, key):
    return ''.join(key[d] for d in raw)


class Fit:
    def __init__(self, words, bank, budgets):
        self.model = Model(words, bank)
        self.budgets = budgets
        self.used = 0
        self.queries = []
        self.first = self.query()
        self.key = self.first['key']
        self.alternative = self.query(different_key=self.key) if self.key is not None else None
        self.unique = self.alternative is not None and self.alternative['status'] == 'UNSAT'

    def query(self, **kwargs):
        remaining = max(0, self.budgets['states_total_per_fit_and_transfers'] - self.used)
        result = self.model.find(**kwargs,
            max_states=min(remaining, self.budgets['states_per_query']),
            local_cap=self.budgets['local_assignments_per_state'])
        self.used += result['states']
        self.queries.append({'exclusion': kwargs, **result})
        return result

    def predict(self, raw):
        missing = sorted(set(raw) - self.model.digits)
        if missing:
            return {'status': 'unknown_digits', 'missing': missing,
                    'form_certified': False, 'chunks_certified': False}
        if self.key is None:
            return {'status': 'no_training_key', 'form_certified': False,
                    'chunks_certified': False}
        form = emit(raw, self.key)
        out = {'form': form, 'chunks': [self.key[d] for d in raw],
               'form_certified': self.unique, 'chunks_certified': self.unique}
        if self.unique:
            return dict(out, status='unique')
        witness = self.alternative['key']
        relevant = {d: self.key[d] for d in set(raw)}
        if witness is None or all(witness[d] == u for d, u in relevant.items()):
            other = self.query(different_key=relevant)
        else:
            other = self.alternative
        if other['status'] == 'UNSAT':
            return dict(out, status='unique_on_target', form_certified=True,
                        chunks_certified=True)
        if other['status'] == 'UNKNOWN':
            return dict(out, status='budget')
        other_form = emit(raw, other['key'])
        out['counterexample_key'] = other['key']
        out['counterexample_form'] = other_form
        if other_form != form:
            return dict(out, status='ambiguous_form')
        form_other = self.query(different_form=(raw, form))
        if form_other['status'] == 'UNSAT':
            return dict(out, status='unique_form_ambiguous_chunks', form_certified=True)
        if form_other['status'] == 'SAT':
            out['counterexample_key'] = form_other['key']
            out['counterexample_form'] = emit(raw, form_other['key'])
            return dict(out, status='ambiguous_form')
        return dict(out, status='budget_form_ambiguous_chunks')


def word_paths(raw, key, bank):
    """Exact lexical DAG with word cuts ONLY at digit-unit boundaries."""
    if set(raw) - set(key):
        return {'status': 'unknown_digits', 'paths': None, 'unique_words': None}
    n = len(raw)
    counts = [0] * (n + 1)
    counts[n] = 1
    edges = {}
    for i in range(n - 1, -1, -1):
        form = ''
        for j in range(i + 1, n + 1):
            form += key[raw[j-1]]
            if len(form) > bank.lengths[-1]:
                break
            labels = bank.reverse.get(form, [])
            if labels and counts[j]:
                edges.setdefault(i, []).append((j, labels))
                counts[i] += len(labels) * counts[j]
    words = None
    if counts[0] == 1:
        words, i = [], 0
        while i < n:
            j, labels = edges[i][0]
            words.extend(labels)
            i = j
    return {'status': 'unique' if counts[0] == 1 else 'ambiguous' if counts[0] else 'no_parse',
            'paths': counts[0], 'unique_words': words}
