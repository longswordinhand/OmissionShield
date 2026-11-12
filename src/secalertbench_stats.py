from __future__ import annotations
import json, math
from pathlib import Path


def wilson(k:int,n:int,z:float=1.959963984540054):
    if not n:return [None,None]
    p=k/n; den=1+z*z/n
    ctr=(p+z*z/(2*n))/den
    half=z*math.sqrt((p*(1-p)+z*z/(4*n))/n)/den
    return [ctr-half,ctr+half]


def analyze(path:Path):
    rows=[json.loads(x) for x in path.read_text(encoding='utf-8').splitlines() if x.strip()]
    comp=[r for r in rows if r.get('label')=='Attack' and r.get('full_correct')]
    vuln=[r for r in comp if r.get('mdo_leq2') is not None]
    random_probs=[]
    for r in vuln:
        k=r['mdo_leq2']
        if k==1:
            trials=r.get('single_omissions',[])
        else:
            trials=r.get('pair_omissions',[])
        target=sum(bool(x.get('target_flip')) for x in trials)
        if trials: random_probs.append(target/len(trials))
    k1=sum(bool(r.get('mdo1')) for r in comp)
    k2=sum(bool(r.get('mdo2')) for r in comp)
    return {
      'n_attack_full_correct':len(comp),
      'n_mdo1':k1,'n_mdo2':k2,'n_vulnerable_leq2':len(vuln),
      'vulnerable_leq2_rate_cond_attack_full_correct':len(vuln)/len(comp) if comp else None,
      'vulnerable_leq2_wilson95':wilson(len(vuln),len(comp)),
      'mdo1_rate_cond_attack_full_correct':k1/len(comp) if comp else None,
      'mdo1_wilson95':wilson(k1,len(comp)),
      'mean_random_hit_probability_at_case_specific_mdo_among_vulnerable':sum(random_probs)/len(random_probs) if random_probs else None,
      'n_random_probability_cases':len(random_probs),
    }


def main():
    root=Path('results/secalertbench')
    files=sorted(root.glob('*_primary_mdo2_trials.jsonl'))
    out={p.name:analyze(p) for p in files}
    # Include one-field/content-only summaries even before pair follow-up.
    for p in sorted(root.glob('*_content_only_summary.json')):
        s=json.loads(p.read_text())
        k=s['n_attack_mdo1'];n=s['attack_full_correct']
        out[p.name]={
          'n_attack_full_correct':n,'n_mdo1':k,
          'mdo1_rate_cond_attack_full_correct':k/n if n else None,
          'mdo1_wilson95':wilson(k,n),
          'attack_full_tpr':s['attack_full_tpr'],
          'attack_full_tpr_wilson95':wilson(n,s['n_attack']),
          'non_attack_full_correct':s['non_attack_full_correct'],
          'non_attack_tnr':s['non_attack_tnr'],
          'non_attack_tnr_wilson95':wilson(s['non_attack_full_correct'],s['n_non_attack']),
        }
    (root/'final_stats.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__':main()
