from __future__ import annotations
import csv, json, math, statistics, time
from pathlib import Path
from src.evidence_dag import CoverageObligation
from src.runtime import TrustedEvidenceRuntime

SIZES_REPEATS=[(10,2000),(100,1000),(1000,300),(10000,50)]
COMMIT_REPEATS=100
KEY=b'phase1-retime-audit-key'

def p95_nearest_rank(xs):
    ys=sorted(xs); return ys[max(0, math.ceil(0.95*len(ys))-1)]

def build_runtime(n:int, omit_last:bool=False):
    ids=[f'e{i:06d}' for i in range(n)]
    rt=TrustedEvidenceRuntime(KEY)
    signed=rt.enumerate_source(f'task-{n}',[(eid,'x') for eid in ids])
    delivered=ids[:-1] if omit_last else ids
    rt.deliver('stage',delivered)
    rt.commit_derived('stage','summary','free-form summary')
    return rt,signed

def run(outdir:Path):
    outdir.mkdir(parents=True,exist_ok=True)
    raw=[]; summary=[]
    for n,reps in SIZES_REPEATS:
        ids=[f'e{i:06d}' for i in range(n)]
        commit=[]
        for i in range(COMMIT_REPEATS):
            s=time.perf_counter_ns(); CoverageObligation.from_source_ids(f'commit-{n}-{i}',ids); us=(time.perf_counter_ns()-s)/1e3
            commit.append(us); raw.append({'phase':'coverage_commitment_build','n_evidence':n,'repeat':i,'microseconds':us,'allow':''})
        rt_full,signed_full=build_runtime(n,False)
        full=[]
        for i in range(reps):
            s=time.perf_counter_ns(); d=rt_full.gate(signed_full,['summary']); us=(time.perf_counter_ns()-s)/1e3
            assert d.allow; full.append(us); raw.append({'phase':'runtime_gate_full_hmac','n_evidence':n,'repeat':i,'microseconds':us,'allow':True})
        rt_omit,signed_omit=build_runtime(n,True)
        omit=[]
        for i in range(reps):
            s=time.perf_counter_ns(); d=rt_omit.gate(signed_omit,['summary']); us=(time.perf_counter_ns()-s)/1e3
            assert not d.allow; omit.append(us); raw.append({'phase':'runtime_gate_omit_hmac','n_evidence':n,'repeat':i,'microseconds':us,'allow':False})
        summary.append({
            'n_evidence':n,'gate_repeats':reps,'commit_repeats':COMMIT_REPEATS,
            'commitment_build_median_us':statistics.median(commit),'commitment_build_p95_us':p95_nearest_rank(commit),
            'gate_full_median_us':statistics.median(full),'gate_full_p95_us':p95_nearest_rank(full),
            'gate_omit_median_us':statistics.median(omit),'gate_omit_p95_us':p95_nearest_rank(omit),
        })
    with (outdir/'timings.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['phase','n_evidence','repeat','microseconds','allow']); w.writeheader(); w.writerows(raw)
    (outdir/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    return summary

if __name__=='__main__':
    print(json.dumps(run(Path('revision_2026-11-10/overhead_retimed')),indent=2))
