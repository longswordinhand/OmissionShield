from __future__ import annotations
import argparse, json, time
from pathlib import Path
from src.secalertbench_eval import load_frozen, visible_fields, render, norm, expected, SEED

def run(dataset: Path, frozen: Path, model_path: str, model_name: str, outdir: Path,
        batch_size: int = 8, view: str = 'primary', max_per_label: int | None = None,
        omissions: bool = False):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    torch.manual_seed(SEED)
    records = load_frozen(dataset, frozen)
    if max_per_label is not None:
        kept=[]; counts={'Attack':0,'Non-Attack':0}
        for r in records:
            lab=r['Label']
            if counts[lab] < max_per_label:
                kept.append(r); counts[lab]+=1
        records=kept

    tokenizer=AutoTokenizer.from_pretrained(model_path, local_files_only=True)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token_id=tokenizer.eos_token_id
    tokenizer.padding_side='left'
    model=AutoModelForCausalLM.from_pretrained(
        model_path, device_map='auto', torch_dtype='auto', local_files_only=True
    )
    model.eval()

    def infer(jobs):
        outputs={}
        for start in range(0,len(jobs),batch_size):
            batch=jobs[start:start+batch_size]
            texts=[]
            for *_,prompt in batch:
                msgs=[{'role':'user','content':prompt}]
                texts.append(tokenizer.apply_chat_template(
                    msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False
                ))
            inp=tokenizer(texts,padding=True,return_tensors='pt')
            inp={k:v.to(model.device) for k,v in inp.items()}
            with torch.inference_mode():
                gen=model.generate(**inp,max_new_tokens=8,do_sample=False)
            pre=inp['input_ids'].shape[1]
            dec=tokenizer.batch_decode(gen[:,pre:],skip_special_tokens=True)
            for (idx,variant,omit,_),txt in zip(batch,dec):
                outputs[(idx,variant,omit)]=txt.strip()
        return outputs

    full_jobs=[]
    for r in records:
        fs=visible_fields(r,view)
        full_jobs.append((r['index'],'full',None,render(r,fs)))
    t0=time.time()
    full_out=infer(full_jobs)
    rows=[]; omit_jobs=[]
    for r in records:
        raw=full_out[(r['index'],'full',None)]
        lab=norm(raw); exp=expected(r['Label']); fs=visible_fields(r,view)
        row={'index':r['index'],'label':r['Label'],'rule_name':r.get('rule_name',''),
             'full_raw':raw,'full_label':lab,'full_correct':lab==exp,'fields':fs}
        rows.append(row)
        if omissions and r['Label']=='Attack' and row['full_correct']:
            for f in fs:
                omit_jobs.append((r['index'],'omit1',f,render(r,[x for x in fs if x!=f])))

    omit_out=infer(omit_jobs) if omit_jobs else {}
    for row in rows:
        omissions_out=[]
        if omissions and row['label']=='Attack' and row['full_correct']:
            for f in row['fields']:
                raw=omit_out[(row['index'],'omit1',f)]; lab=norm(raw)
                omissions_out.append({'field':f,'raw':raw,'label':lab,'target_flip':lab=='CLOSE'})
        row['single_omissions']=omissions_out
        row['mdo1']=any(x['target_flip'] for x in omissions_out)
        row['decisive_fields']=[x['field'] for x in omissions_out if x['target_flip']]

    atk=[r for r in rows if r['label']=='Attack']; non=[r for r in rows if r['label']=='Non-Attack']
    comp=[r for r in atk if r['full_correct']]
    summary={
        'dataset':'SecAlertBench','view':view,'model':model_name,'seed':SEED,
        'diagnostic_max_per_label':max_per_label,
        'n_total':len(rows),'n_attack':len(atk),'n_non_attack':len(non),
        'attack_full_correct':len(comp),'attack_full_tpr':len(comp)/len(atk) if atk else None,
        'non_attack_full_correct':sum(r['full_correct'] for r in non),
        'non_attack_tnr':sum(r['full_correct'] for r in non)/len(non) if non else None,
        'overall_full_accuracy':sum(r['full_correct'] for r in rows)/len(rows) if rows else None,
        'n_attack_mdo1':sum(r.get('mdo1',False) for r in comp) if omissions else None,
        'mdo1_rate_cond_attack_full_correct':(
            sum(r.get('mdo1',False) for r in comp)/len(comp) if omissions and comp else None
        ),
        'n_omission_prompts':len(omit_jobs),
        'elapsed_seconds':time.time()-t0,
    }
    outdir.mkdir(parents=True,exist_ok=True)
    suffix=f'_diag{max_per_label}' if max_per_label is not None else ''
    mode='_single' if omissions else '_full'
    (outdir/f'{model_name}_{view}{suffix}{mode}_trials.jsonl').write_text(
        ''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in rows),encoding='utf-8')
    (outdir/f'{model_name}_{view}{suffix}{mode}_summary.json').write_text(
        json.dumps(summary,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(summary,indent=2,sort_keys=True))

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--dataset',default='data/public/secalertbench/secalertbench.json')
    p.add_argument('--frozen',default='results/secalertbench/FROZEN_COHORT.json')
    p.add_argument('--model-path',required=True); p.add_argument('--model-name',required=True)
    p.add_argument('--out-dir',default='results/secalertbench_highcompetence')
    p.add_argument('--batch-size',type=int,default=8)
    p.add_argument('--view',choices=['primary','content_only'],default='primary')
    p.add_argument('--max-per-label',type=int)
    p.add_argument('--omissions',action='store_true')
    a=p.parse_args()
    run(Path(a.dataset),Path(a.frozen),a.model_path,a.model_name,Path(a.out_dir),
        a.batch_size,a.view,a.max_per_label,a.omissions)
