from __future__ import annotations
import json
from pathlib import Path
from src.tqrg_real_bench import select_candidates, fetch_commit

OUT=Path('results/tqrg_holdout')

def freeze_and_fetch():
    OUT.mkdir(parents=True,exist_ok=True)
    first50=select_candidates(50)
    cohort_a=first50[:20]
    cohort_b=first50[20:50]
    freeze={
      'selection_rule':'same deterministic TQRG metadata-only rule as cohort A',
      'note':'Cohort B frozen before its GitHub patches were retrieved or any cohort-B model outputs were observed.',
      'cohort_a_shas':[c.sha for c in cohort_a],
      'cohort_b_n':len(cohort_b),
      'candidates':[c.__dict__ for c in cohort_b],
    }
    (OUT/'FROZEN_COHORT_B.json').write_text(json.dumps(freeze,indent=2,sort_keys=True)+'\n')
    rows=[]; errors=[]
    for c in cohort_b:
        try:
            d=fetch_commit(c)
            if not any(f.get('patch') for f in d['files']):
                errors.append({'sha':c.sha,'reason':'no textual patch'}); continue
            rows.append(d)
        except Exception as e:
            errors.append({'sha':c.sha,'reason':f'{type(e).__name__}: {e}'})
    with (OUT/'commits.jsonl').open('w',encoding='utf-8') as f:
        for r in rows:f.write(json.dumps(r,sort_keys=True)+'\n')
    summary={'frozen_n':len(cohort_b),'retrieved':len(rows),'excluded':len(errors),'errors':errors}
    (OUT/'fetch_summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
    print(json.dumps(summary,indent=2,sort_keys=True))

if __name__=='__main__':freeze_and_fetch()
