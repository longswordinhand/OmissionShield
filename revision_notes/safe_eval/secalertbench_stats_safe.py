import argparse,json
from pathlib import Path
from _guard import guarded_out
from src.secalertbench_stats import analyze,wilson
p=argparse.ArgumentParser(); p.add_argument('--input-root',default='results/secalertbench'); p.add_argument('--out-file',required=True); p.add_argument('--force',action='store_true'); a=p.parse_args(); root=Path(a.input_root); out={x.name:analyze(x) for x in sorted(root.glob('*_primary_mdo2_trials.jsonl'))}
for x in sorted(root.glob('*_content_only_summary.json')):
 s=json.loads(x.read_text()); k=s['n_attack_mdo1']; n=s['attack_full_correct']; out[x.name]={'n_attack_full_correct':n,'n_mdo1':k,'mdo1_rate_cond_attack_full_correct':k/n if n else None,'mdo1_wilson95':wilson(k,n),'attack_full_tpr':s['attack_full_tpr'],'attack_full_tpr_wilson95':wilson(n,s['n_attack']),'non_attack_full_correct':s['non_attack_full_correct'],'non_attack_tnr':s['non_attack_tnr'],'non_attack_tnr_wilson95':wilson(s['non_attack_full_correct'],s['n_non_attack'])}
o=guarded_out(a.out_file,a.force); o.parent.mkdir(parents=True,exist_ok=True); o.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(json.dumps(out,indent=2,sort_keys=True))
