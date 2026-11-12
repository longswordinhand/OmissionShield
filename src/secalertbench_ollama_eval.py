from __future__ import annotations
import argparse, json, time
from pathlib import Path
from src.phase0c_llm import call_ollama
from src.secalertbench_eval import load_frozen, visible_fields, render, norm, expected, SEED


def run(dataset:Path,frozen:Path,outdir:Path,model_name='qwen3_8_2b_q4km',view='primary'):
    records=load_frozen(dataset,frozen)
    rows=[]; omission_count=0
    t0=time.time()
    for j,r in enumerate(records,1):
        fs=visible_fields(r,view)
        full_raw=call_ollama('/no_think\n'+render(r,fs)); full_label=norm(full_raw); full_correct=full_label==expected(r['Label'])
        omissions=[]
        if r['Label']=='Attack' and full_correct:
            for f in fs:
                raw=call_ollama('/no_think\n'+render(r,[x for x in fs if x!=f])); lab=norm(raw); omission_count+=1
                omissions.append({'field':f,'raw':raw,'label':lab,'target_flip':lab=='CLOSE'})
        rows.append({'index':r['index'],'label':r['Label'],'rule_name':r.get('rule_name',''),'full_raw':full_raw,'full_label':full_label,'full_correct':full_correct,'fields':fs,'single_omissions':omissions,'mdo1':any(x['target_flip'] for x in omissions),'decisive_fields':[x['field'] for x in omissions if x['target_flip']]})
        print(f"[{j}/{len(records)}] idx={r['index']} label={r['Label']} full={full_label} correct={full_correct} mdo1={rows[-1]['mdo1']}",flush=True)
    outdir.mkdir(parents=True,exist_ok=True)
    trials=outdir/f'{model_name}_{view}_trials.jsonl'; trials.write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in rows),encoding='utf-8')
    atk=[r for r in rows if r['label']=='Attack']; non=[r for r in rows if r['label']=='Non-Attack']; comp=[r for r in atk if r['full_correct']]
    s={'dataset':'SecAlertBench','view':view,'model':model_name,'seed':SEED,'n_total':len(rows),'n_attack':len(atk),'n_non_attack':len(non),'attack_full_correct':len(comp),'attack_full_tpr':len(comp)/len(atk),'non_attack_full_correct':sum(r['full_correct'] for r in non),'non_attack_tnr':sum(r['full_correct'] for r in non)/len(non),'overall_full_accuracy':sum(r['full_correct'] for r in rows)/len(rows),'n_attack_mdo1':sum(r['mdo1'] for r in comp),'mdo1_rate_cond_attack_full_correct':sum(r['mdo1'] for r in comp)/len(comp) if comp else None,'n_omission_prompts':omission_count,'elapsed_seconds':time.time()-t0}
    (outdir/f'{model_name}_{view}_summary.json').write_text(json.dumps(s,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(s,indent=2,sort_keys=True))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--dataset',default='data/public/secalertbench/secalertbench.json');p.add_argument('--frozen',default='results/secalertbench/FROZEN_COHORT.json');p.add_argument('--out-dir',default='results/secalertbench');p.add_argument('--model-name',default='qwen3_8_2b_q4km');p.add_argument('--view',choices=['primary','content_only'],default='primary');a=p.parse_args();run(Path(a.dataset),Path(a.frozen),Path(a.out_dir),a.model_name,a.view)
