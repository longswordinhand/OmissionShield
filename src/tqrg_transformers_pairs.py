from __future__ import annotations
import argparse,json,re,time
from itertools import combinations
from pathlib import Path

from src.tqrg_transformers_eval import load_all, textual, render, norm


def run(model_path:str,model_name:str,outdir:Path,batch_size:int=2):
    import torch
    from transformers import AutoProcessor,Qwen2_5_VLForConditionalGeneration
    base_path=outdir/f'{model_name}_trials.jsonl'
    base=[json.loads(x) for x in base_path.read_text().splitlines() if x.strip()]
    bysha={r['sha']:r for r in base}
    commits=load_all()
    jobs=[]
    for c in commits:
        b=bysha[c['sha']]
        if not b['full_correct'] or b['mdo1']:
            continue
        fs=textual(c)
        for pair in combinations(range(len(fs)),2):
            kept=[f for j,f in enumerate(fs) if j not in pair]
            omitted=[fs[j]['filename'] for j in pair]
            jobs.append((c['sha'],omitted,render(kept)))
    torch.manual_seed(20260824)
    t0=time.time()
    model=Qwen2_5_VLForConditionalGeneration.from_pretrained(model_path,torch_dtype=torch.bfloat16,device_map='auto')
    processor=AutoProcessor.from_pretrained(model_path); processor.tokenizer.padding_side='left'
    outputs=[]
    for start in range(0,len(jobs),batch_size):
        batch=jobs[start:start+batch_size]; texts=[]
        for _,_,prompt in batch:
            msgs=[{'role':'user','content':[{'type':'text','text':prompt}]}]
            texts.append(processor.apply_chat_template(msgs,tokenize=False,add_generation_prompt=True))
        inp=processor(text=texts,padding=True,return_tensors='pt'); inp={k:(v.to(model.device) if hasattr(v,'to') else v) for k,v in inp.items()}
        with torch.inference_mode():gen=model.generate(**inp,max_new_tokens=10,do_sample=False)
        pre=inp['input_ids'].shape[1]; dec=processor.batch_decode(gen[:,pre:],skip_special_tokens=True)
        for (sha,omitted,_),txt in zip(batch,dec):outputs.append({'sha':sha,'omitted_files':omitted,'raw':txt.strip(),'label':norm(txt),'target_flip':norm(txt)=='NO_SECURITY_FIX'})
    pairs_by={}
    for r in outputs:pairs_by.setdefault(r['sha'],[]).append(r)
    rows=[]
    for b in base:
        pairs=pairs_by.get(b['sha'],[])
        mdo2=b['full_correct'] and (not b['mdo1']) and any(x['target_flip'] for x in pairs)
        rows.append({**b,'pair_omissions':pairs,'mdo2':mdo2,'mdo_leq2':1 if b['mdo1'] else (2 if mdo2 else None)})
    with (outdir/f'{model_name}_mdo2_trials.jsonl').open('w') as f:
        for r in rows:f.write(json.dumps(r,sort_keys=True)+'\n')
    comp=[r for r in rows if r['full_correct']]; vuln=[r for r in comp if r['mdo_leq2'] is not None]
    summary={'model':model_name,'n_commits':len(rows),'n_full_correct':len(comp),'n_mdo1':sum(r['mdo1'] for r in comp),'n_mdo2':sum(r['mdo2'] for r in comp),'n_vulnerable_leq2':len(vuln),'vulnerable_leq2_rate_cond_full_correct':len(vuln)/len(comp),'n_pair_prompts':len(jobs),'elapsed_seconds':time.time()-t0}
    (outdir/f'{model_name}_mdo2_summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
    print(json.dumps(summary,indent=2,sort_keys=True))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--model-path',required=True);p.add_argument('--model-name',required=True);p.add_argument('--batch-size',type=int,default=2);p.add_argument('--out-dir',default='results/tqrg_crossmodel');a=p.parse_args();run(a.model_path,a.model_name,Path(a.out_dir),a.batch_size)
