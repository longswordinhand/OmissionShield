from __future__ import annotations
import json, math
from pathlib import Path
from math import comb


def wilson(k:int,n:int,z:float=1.959963984540054)->tuple[float,float]:
    if n==0:return (float('nan'),float('nan'))
    p=k/n; den=1+z*z/n
    center=(p+z*z/(2*n))/den
    half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return center-half,center+half


def load(path:Path):
    return [json.loads(x) for x in path.read_text().splitlines() if x.strip()]


def cohort_summary(rows):
    comp=[r for r in rows if r['full_correct']]
    mdo1=sum(r['mdo_leq2']==1 for r in comp)
    mdo2=sum(r['mdo_leq2']==2 for r in comp)
    vuln=mdo1+mdo2
    probs=[]
    for r in comp:
        k=r['mdo_leq2']
        if k in (1,2):
            denom=comb(r['n_textual_files'],k)
            probs.append(len(r['decisive_omissions'])/denom)
    return {
      'n':len(rows),'full_correct':len(comp),'full_accuracy':len(comp)/len(rows),
      'full_accuracy_ci95':wilson(len(comp),len(rows)),
      'mdo1':mdo1,'mdo2':mdo2,'vulnerable_leq2':vuln,
      'vulnerable_leq2_rate_cond_full':vuln/len(comp) if comp else None,
      'vulnerable_leq2_ci95':wilson(vuln,len(comp)) if comp else None,
      'mean_random_hit_probability_at_mdo_among_vulnerable':sum(probs)/len(probs) if probs else None,
    }


def run(out:Path):
    a=load(Path('results/tqrg_real/llm_qwen3/trials.jsonl'))
    b=load(Path('results/tqrg_holdout/llm_qwen3/trials.jsonl'))
    obj={'cohort_A':cohort_summary(a),'cohort_B':cohort_summary(b),'pooled_descriptive':cohort_summary(a+b)}
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')
    print(json.dumps(obj,indent=2,sort_keys=True))

if __name__=='__main__':run(Path('results/tqrg_combined_stats.json'))
