#!/usr/bin/env python3
"""Reproduce reviewed upstream validator and run falsifying negative controls."""
import contextlib,io,json,pathlib,random,runpy
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
    source=ROOT/'sources/arturo/scripts/validate_solution.py'
    random.seed(469)
    log=io.StringIO()
    with contextlib.redirect_stdout(log):
        runpy.run_path(str(source),run_name='__main__')
    (ROOT/'results/upstream_arturo_validator.log').write_text(log.getvalue())
    ns=runpy.run_path(str(source))
    # Globals belong to returned functions; change the mapping, keeping source tests identical.
    funcs=[ns['test_overlap_consistency'],ns['test_repeating_sequences']]
    results=[]
    for trial in range(100):
        codes=list(ns['v7'])
        mapping={c:random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ') for c in codes}
        row={'trial':trial}
        with contextlib.redirect_stdout(io.StringIO()):
            for f in funcs:
                f.__globals__['v7']=mapping
                row[f.__name__]=f()
        results.append(row)
    out={'seed':469,'controls':100,'random_mapping_passes':{f.__name__:sum(r[f.__name__] for r in results) for f in funcs},
         'interpretation':'These source tests compare the same substring decoded with the same mapping against itself. They must pass for any deterministic mapping; zero ability to distinguish translations from random assignments.',
         'other_limitations':['Upstream IC measures nonuniformity, not German identification.',
           'Upstream permutation control compares a fitted mapping to unfitted random maps on reused books; does not account for mapping search, manual repairs or holdout.',
           'Original validation suite reproduced verbatim with fixed seed; its PASS conclusions are not endorsed.']}
    (ROOT/'results/upstream_validation_audit.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))
if __name__=='__main__':main()
