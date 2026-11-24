#!/usr/bin/env python3
"""Requirements-based evidence disposition; cannot infer semantic truth from hashes."""
from pathlib import Path
import json
from round30_audit import ROOT, digest


def qualifies(requirements,names):
    if set(requirements)!=set(names):raise ValueError('Missing or undeclared evidence criterion')
    if any(v not in ('met','not_established','contradicted') for v in requirements.values()):
        raise ValueError('Evidence statuses must be explicit')
    return all(requirements[n]=='met' for n in names)


def adjudicate(catalog):
    translations=[c['id'] for c in catalog['candidate_families'] if qualifies(c['requirements'],catalog['translation_requirements'])]
    generators=[c['id'] for c in catalog['nontext_claims'] if qualifies(c['requirements'],catalog['nontext_requirements'])]
    # T and G can coexist for different sources; never silently merge their scopes.
    outcome='T_and_G_require_separate_scopes' if translations and generators else 'T_scoped' if translations else 'G_scoped' if generators else 'I_inconclusive'
    return {'mission_outcome':outcome,'qualified_translation_ids':translations,
            'qualified_original_nontext_generator_ids':generators,
            'translation_validated':bool(translations),
            'original_nontextual_generator_authenticated':bool(generators)}


def build():
    catalog=json.loads((ROOT/'data/round30_evidence_catalog.json').read_text())
    result=adjudicate(catalog)
    paths=set(catalog['historical_decision_sources'])
    for c in catalog['candidate_families']+catalog['nontext_claims']:paths.update(c['evidence'])
    references={p:digest(ROOT/p) for p in sorted(paths)}
    r23=json.loads((ROOT/'results/round23_targets.json').read_text())
    pending=[{'source':r['id'],'family':r['family'],'returned_lexical_keys':len(r['keys']),'status':'bounded_search_not_exhaustive'} for r in r23['targets'] if not r['complete']]
    return {'round':30,**result,'batch_completed_through_round':30,
        'remaining_rounds_in_mission_plan_v2':[],'translation_mission_closed':False,
        'new_semantic_candidates':[],'pending_prior_main_fits':pending,
        'evidence_sha256':references,
        'names_and_matrices':'Retain scoped rounds25/26/28 decisions; no new measurements, rename coincidence or cipher key authenticated.',
        'limits':['Evidence requirement statuses are explicit research judgments grounded in linked audits, not an automated English oracle.',
                  'No new blinded semantic test or newly authenticated original game production process.',
                  'Current inconclusive disposition cannot prove that no possible numeric-to-text function exists.']}


if __name__=='__main__':
    path=ROOT/'results/round30_adjudication.json'
    if path.exists():raise ValueError('Refuse to replace adjudication')
    result=build();path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(result['mission_outcome'],'qualified translations:',len(result['qualified_translation_ids']))
