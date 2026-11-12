from __future__ import annotations
import argparse,json,re,time
from pathlib import Path
from typing import Any


def load_all() -> list[dict[str,Any]]:
    paths=[Path('results/tqrg_real/commits.jsonl'),Path('results/tqrg_holdout/commits.jsonl')]
    out=[]
    for p in paths:
        out += [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
    return out


def textual(c):return [f for f in c['files'] if f.get('patch')]

def render(files):
    chunks=[f"FILE {i}: {f['filename']}\nPATCH:\n{f['patch']}" for i,f in enumerate(files,1)]
    return (
      "You are reviewing a software commit using only the changed-file patches below. "
      "Decide whether the patch contains a security-relevant vulnerability fix (for example memory safety, authentication/authorization, injection, cryptographic validation, information disclosure, or denial of service caused by unsafe input handling). "
      "Return exactly SECURITY_FIX or NO_SECURITY_FIX and no explanation.\n\n"+'\n\n'.join(chunks))

def norm(s):
    u=s.upper()
    if re.search(r'\bNO_SECURITY_FIX\b',u):return 'NO_SECURITY_FIX'
    if re.search(r'\bSECURITY_FIX\b',u):return 'SECURITY_FIX'
    return 'UNPARSEABLE'

def run(model_path:str,model_name:str,outdir:Path,batch_size:int=2):
    import torch
    from transformers import AutoProcessor,Qwen2_5_VLForConditionalGeneration
    torch.manual_seed(20260824)
    commits=load_all()
    jobs=[]
    for c in commits:
        fs=textual(c)
        jobs.append((c['sha'],'full',None,render(fs)))
        for j,f in enumerate(fs):
            jobs.append((c['sha'],'omit1',f['filename'],render([x for k,x in enumerate(fs) if k!=j])))
    t0=time.time()
    model=Qwen2_5_VLForConditionalGeneration.from_pretrained(model_path,torch_dtype=torch.bfloat16,device_map='auto')
    processor=AutoProcessor.from_pretrained(model_path); processor.tokenizer.padding_side='left'
    outputs={}
    for start in range(0,len(jobs),batch_size):
        batch=jobs[start:start+batch_size]; texts=[]
        for *_,prompt in batch:
            messages=[{'role':'user','content':[{'type':'text','text':prompt}]}]
            texts.append(processor.apply_chat_template(messages,tokenize=False,add_generation_prompt=True))
        inp=processor(text=texts,padding=True,return_tensors='pt')
        inp={k:(v.to(model.device) if hasattr(v,'to') else v) for k,v in inp.items()}
        with torch.inference_mode():gen=model.generate(**inp,max_new_tokens=10,do_sample=False)
        pre=inp['input_ids'].shape[1]
        dec=processor.batch_decode(gen[:,pre:],skip_special_tokens=True)
        for (sha,variant,omit,_),txt in zip(batch,dec):outputs[(sha,variant,omit)]=txt.strip()
    rows=[]
    for c in commits:
        fs=textual(c); full_raw=outputs[(c['sha'],'full',None)]; full=norm(full_raw)
        omits=[]
        for f in fs:
            raw=outputs[(c['sha'],'omit1',f['filename'])]; lab=norm(raw)
            omits.append({'file':f['filename'],'raw':raw,'label':lab,'target_flip':full=='SECURITY_FIX' and lab=='NO_SECURITY_FIX'})
        rows.append({'cve_id':c['cve_id'],'project':c['project'],'sha':c['sha'],'n_textual_files':len(fs),'full_raw':full_raw,'full_label':full,'full_correct':full=='SECURITY_FIX','single_omissions':omits,'mdo1':full=='SECURITY_FIX' and any(x['target_flip'] for x in omits)})
    outdir.mkdir(parents=True,exist_ok=True)
    with (outdir/f'{model_name}_trials.jsonl').open('w') as f:
        for r in rows:f.write(json.dumps(r,sort_keys=True)+'\n')
    comp=[r for r in rows if r['full_correct']]; mdo1=sum(r['mdo1'] for r in comp)
    summary={'model':model_name,'n_commits':len(rows),'n_full_correct':len(comp),'full_accuracy':len(comp)/len(rows),'n_mdo1':mdo1,'mdo1_rate_cond_full_correct':mdo1/len(comp) if comp else None,'elapsed_seconds':time.time()-t0,'n_prompts':len(jobs)}
    (outdir/f'{model_name}_summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
    print(json.dumps(summary,indent=2,sort_keys=True))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--model-path',required=True);p.add_argument('--model-name',required=True);p.add_argument('--batch-size',type=int,default=2);p.add_argument('--out-dir',default='results/tqrg_crossmodel');a=p.parse_args();run(a.model_path,a.model_name,Path(a.out_dir),a.batch_size)
