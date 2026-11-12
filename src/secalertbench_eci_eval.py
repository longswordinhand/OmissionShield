from __future__ import annotations
import json
from pathlib import Path
from src.runtime import TrustedEvidenceRuntime
from src.secalertbench_eval import ALL_FIELDS, load_frozen

KEY=b'omissionshield-secalertbench-eci-key'

def run(dataset=Path('data/public/secalertbench/secalertbench.json'), frozen=Path('results/secalertbench/FROZEN_COHORT.json'), outdir=Path('results/secalertbench/eci')):
    records=load_frozen(dataset,frozen)
    outdir.mkdir(parents=True,exist_ok=True)
    trials=[]
    complete_ok=0
    exact=0
    detected=0
    for r in records:
        items=[(f'field:{f}', json.dumps(r.get(f),ensure_ascii=False,sort_keys=True)) for f in ALL_FIELDS]
        rt=TrustedEvidenceRuntime(KEY)
        signed=rt.enumerate_source(f"alert:{r['index']}",items)
        source_handles=[eid for eid,_ in items]
        rt.deliver('triage',source_handles)
        root=rt.commit_derived('triage','triage:summary','summary')
        dec=rt.gate(signed,[root])
        complete_ok += int(dec.allow)
        for omit in source_handles:
            rt2=TrustedEvidenceRuntime(KEY)
            signed2=rt2.enumerate_source(f"alert:{r['index']}",items)
            delivered=[h for h in source_handles if h!=omit]
            rt2.deliver('triage',delivered)
            root2=rt2.commit_derived('triage','triage:summary','summary')
            d=rt2.gate(signed2,[root2])
            detected += int(not d.allow)
            exact += int(d.missing_ids==frozenset([omit]))
            trials.append({'index':r['index'],'label':r['Label'],'omitted':omit,'allow':d.allow,'missing':sorted(d.missing_ids),'exact':d.missing_ids==frozenset([omit])})
    summary={
      'n_alerts':len(records),'n_fields_per_alert':len(ALL_FIELDS),
      'n_complete':len(records),'complete_accept_rate':complete_ok/len(records),
      'n_single_field_suppressions':len(trials),
      'suppression_detection_rate':detected/len(trials),
      'exact_missing_id_rate':exact/len(trials),
    }
    (outdir/'trials.jsonl').write_text(''.join(json.dumps(x,sort_keys=True)+'\n' for x in trials),encoding='utf-8')
    (outdir/'summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(summary,indent=2,sort_keys=True))

if __name__=='__main__': run()
