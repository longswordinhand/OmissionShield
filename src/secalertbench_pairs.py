from __future__ import annotations
import argparse, json, time
from itertools import combinations
from pathlib import Path
from src.secalertbench_eval import load_frozen, render, norm, SEED


def load_trials(path:Path):
    return [json.loads(x) for x in path.read_text(encoding='utf-8').splitlines() if x.strip()]


def run_transformers(dataset:Path,frozen:Path,single_trials:Path,model_path:str,model_name:str,outdir:Path,batch_size:int=4,view='primary'):
    import torch
    from transformers import AutoProcessor,Qwen2_5_VLForConditionalGeneration
    rows=load_trials(single_trials); records={r['index']:r for r in load_frozen(dataset,frozen)}
    jobs=[]
    for r in rows:
        if r['label']!='Attack' or not r['full_correct'] or r['mdo1']: continue
        rec=records[r['index']]
        for pair in combinations(r['fields'],2):
            kept=[f for f in r['fields'] if f not in pair]
            jobs.append((r['index'],tuple(pair),render(rec,kept)))
    torch.manual_seed(SEED)
    t0=time.time()
    model=Qwen2_5_VLForConditionalGeneration.from_pretrained(model_path,torch_dtype=torch.bfloat16,device_map='auto')
    model.generation_config.temperature=None; model.generation_config.top_p=None; model.generation_config.top_k=None
    processor=AutoProcessor.from_pretrained(model_path); processor.tokenizer.padding_side='left'
    outputs=[]
    for start in range(0,len(jobs),batch_size):
        batch=jobs[start:start+batch_size]; texts=[]
        for _,_,prompt in batch:
            msgs=[{'role':'user','content':[{'type':'text','text':prompt}]}]
            texts.append(processor.apply_chat_template(msgs,tokenize=False,add_generation_prompt=True))
        inp=processor(text=texts,padding=True,return_tensors='pt'); inp={k:(v.to(model.device) if hasattr(v,'to') else v) for k,v in inp.items()}
        with torch.inference_mode(): gen=model.generate(**inp,max_new_tokens=10,do_sample=False)
        pre=inp['input_ids'].shape[1]; dec=processor.batch_decode(gen[:,pre:],skip_special_tokens=True)
        for (idx,pair,_),txt in zip(batch,dec): outputs.append({'index':idx,'omitted_fields':list(pair),'raw':txt.strip(),'label':norm(txt),'target_flip':norm(txt)=='CLOSE'})
    by={}
    for x in outputs:by.setdefault(x['index'],[]).append(x)
    final=[]
    for r in rows:
        pairs=by.get(r['index'],[]); mdo2=(r['label']=='Attack' and r['full_correct'] and not r['mdo1'] and any(x['target_flip'] for x in pairs))
        final.append({**r,'pair_omissions':pairs,'mdo2':mdo2,'mdo_leq2':1 if r['mdo1'] else (2 if mdo2 else None)})
    outdir.mkdir(parents=True,exist_ok=True)
    (outdir/f'{model_name}_{view}_mdo2_trials.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False,sort_keys=True)+'\n' for x in final),encoding='utf-8')
    comp=[r for r in final if r['label']=='Attack' and r['full_correct']]; vuln=[r for r in comp if r['mdo_leq2'] is not None]
    s={'dataset':'SecAlertBench','model':model_name,'view':view,'n_attack_full_correct':len(comp),'n_mdo1':sum(r['mdo1'] for r in comp),'n_mdo2':sum(r['mdo2'] for r in comp),'n_vulnerable_leq2':len(vuln),'vulnerable_leq2_rate_cond_attack_full_correct':len(vuln)/len(comp) if comp else None,'n_pair_prompts':len(jobs),'elapsed_seconds':time.time()-t0,'seed':SEED}
    (outdir/f'{model_name}_{view}_mdo2_summary.json').write_text(json.dumps(s,indent=2,sort_keys=True)+'\n',encoding='utf-8');print(json.dumps(s,indent=2,sort_keys=True))


def run_ollama(dataset:Path,frozen:Path,single_trials:Path,model_name:str,outdir:Path,view='primary'):
    from src.phase0c_llm import call_ollama
    rows=load_trials(single_trials); records={r['index']:r for r in load_frozen(dataset,frozen)}; outputs=[]; t0=time.time(); jobs=0
    for i,r in enumerate(rows,1):
        if r['label']!='Attack' or not r['full_correct'] or r['mdo1']: continue
        rec=records[r['index']]
        for pair in combinations(r['fields'],2):
            raw=call_ollama('/no_think\n'+render(rec,[f for f in r['fields'] if f not in pair]));lab=norm(raw);jobs+=1
            outputs.append({'index':r['index'],'omitted_fields':list(pair),'raw':raw,'label':lab,'target_flip':lab=='CLOSE'})
        print(f"pair record {i}/{len(rows)} idx={r['index']}",flush=True)
    by={}
    for x in outputs:by.setdefault(x['index'],[]).append(x)
    final=[]
    for r in rows:
        pairs=by.get(r['index'],[]);mdo2=(r['label']=='Attack' and r['full_correct'] and not r['mdo1'] and any(x['target_flip'] for x in pairs))
        final.append({**r,'pair_omissions':pairs,'mdo2':mdo2,'mdo_leq2':1 if r['mdo1'] else (2 if mdo2 else None)})
    outdir.mkdir(parents=True,exist_ok=True)
    (outdir/f'{model_name}_{view}_mdo2_trials.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False,sort_keys=True)+'\n' for x in final),encoding='utf-8')
    comp=[r for r in final if r['label']=='Attack' and r['full_correct']];vuln=[r for r in comp if r['mdo_leq2'] is not None]
    s={'dataset':'SecAlertBench','model':model_name,'view':view,'n_attack_full_correct':len(comp),'n_mdo1':sum(r['mdo1'] for r in comp),'n_mdo2':sum(r['mdo2'] for r in comp),'n_vulnerable_leq2':len(vuln),'vulnerable_leq2_rate_cond_attack_full_correct':len(vuln)/len(comp) if comp else None,'n_pair_prompts':jobs,'elapsed_seconds':time.time()-t0,'seed':SEED}
    (outdir/f'{model_name}_{view}_mdo2_summary.json').write_text(json.dumps(s,indent=2,sort_keys=True)+'\n',encoding='utf-8');print(json.dumps(s,indent=2,sort_keys=True))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--dataset',default='data/public/secalertbench/secalertbench.json');p.add_argument('--frozen',default='results/secalertbench/FROZEN_COHORT.json');p.add_argument('--single-trials',required=True);p.add_argument('--model-name',required=True);p.add_argument('--model-path');p.add_argument('--backend',choices=['transformers','ollama'],required=True);p.add_argument('--batch-size',type=int,default=4);p.add_argument('--view',default='primary');p.add_argument('--out-dir',default='results/secalertbench');a=p.parse_args()
    if a.backend=='transformers':
        if not a.model_path: raise SystemExit('--model-path required')
        run_transformers(Path(a.dataset),Path(a.frozen),Path(a.single_trials),a.model_path,a.model_name,Path(a.out_dir),a.batch_size,a.view)
    else: run_ollama(Path(a.dataset),Path(a.frozen),Path(a.single_trials),a.model_name,Path(a.out_dir),a.view)
