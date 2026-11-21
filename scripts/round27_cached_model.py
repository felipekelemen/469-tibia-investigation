"""Execution optimization: memoize lexical filtering between exact queries.

The filtered domain at a partial key is root-domain intersection with that
key's constraints; it is independent of the path and query exclusion.
Preserve DFS order, budgets and all returned states; never cache query answers.
The original frozen Model.find remains the unoptimized replay reference.
"""
from round27_witness_solver import Model, emit, key_tuple, word_extensions, word_pattern

ORIGINAL_FIND = Model.find


def filtered_at(model, key, domains):
    if not hasattr(model, '_filtered_cache'):
        model._filtered_cache = {}
    kt = key_tuple(key)
    if kt in model._filtered_cache:
        return model._filtered_cache[kt]
    filtered, choices = [], []
    for i, (raw, fs) in enumerate(zip(model.words, domains)):
        if all(d in key for d in raw):
            form = emit(raw, key)
            if form not in fs:
                model._filtered_cache[kt] = None
                return None
            matches = (form,)
        else:
            pattern = word_pattern(raw, model.bank.minimum, model.bank.maximum, key)
            matches = tuple(f for f in fs if pattern.fullmatch(f))
            if not matches:
                model._filtered_cache[kt] = None
                return None
            choices.append((len(matches), i))
        filtered.append(matches)
    model._filtered_cache[kt] = (filtered, choices)
    return filtered, choices


def cached_find(self, different_key=None, different_form=None,
                max_states=2000, local_cap=20000):
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
        cached = filtered_at(self, key, domains)
        if cached is None:
            return
        filtered, choices = cached
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


def enable():
    Model.find = cached_find


def disable():
    Model.find = ORIGINAL_FIND
