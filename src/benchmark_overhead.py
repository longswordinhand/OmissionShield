from __future__ import annotations

import json
import statistics
import time
from pathlib import Path

from src.evidence_dag import CoverageObligation, EvidenceDAG, why_not_gate


def one_size(n: int, repeats: int) -> dict:
    ids=[f'e{i:06d}' for i in range(n)]
    t0=time.perf_counter()
    obl=CoverageObligation.from_source_ids(f'task-{n}',ids)
    commit_us=(time.perf_counter()-t0)*1e6

    dag=EvidenceDAG()
    for eid in ids:
        dag.add_source(eid,payload='x')
    dag.add_derived('summary',ids,payload='free-form summary')

    full=[]
    for _ in range(repeats):
        s=time.perf_counter_ns()
        dec=why_not_gate(dag,obl,['summary'],obl.source_root)
        full.append((time.perf_counter_ns()-s)/1e3)
        assert dec.allow

    # Suppress one item by constructing a derived node that structurally omits it.
    dag2=EvidenceDAG()
    for eid in ids:
        dag2.add_source(eid,payload='x')
    dag2.add_derived('summary',ids[:-1],payload='summary')
    detect=[]
    for _ in range(repeats):
        s=time.perf_counter_ns()
        dec=why_not_gate(dag2,obl,['summary'],obl.source_root)
        detect.append((time.perf_counter_ns()-s)/1e3)
        assert not dec.allow

    return {
        'n_evidence':n,
        'commitment_build_us':commit_us,
        'gate_full_median_us':statistics.median(full),
        'gate_full_p95_us':sorted(full)[int(0.95*(len(full)-1))],
        'gate_omit_median_us':statistics.median(detect),
        'gate_omit_p95_us':sorted(detect)[int(0.95*(len(detect)-1))],
        'repeats':repeats,
    }


def run(out: Path) -> dict:
    out.mkdir(parents=True,exist_ok=True)
    rows=[]
    for n,reps in [(10,2000),(100,1000),(1000,300),(10000,50)]:
        rows.append(one_size(n,reps))
    (out/'overhead.json').write_text(json.dumps(rows,indent=2)+'\n')
    print(json.dumps(rows,indent=2))
    return {'rows':rows}

if __name__=='__main__':
    run(Path('results/overhead'))
