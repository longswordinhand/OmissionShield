from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import time
from pathlib import Path
from typing import Any

SEED = 20260825
ALL_FIELDS = [
    'attack_type','dip','dport','host','kill_chain_all','method','parameter','proto',
    'req_body','req_header','rsp_body','rsp_header','rsp_status','rule_name','sip','sport','uri','xff'
]
CONTENT_ONLY_EXCLUDE = {'attack_type','kill_chain_all','rule_name'}


def canon_hash(record: dict[str, Any]) -> str:
    payload = json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')
    return hashlib.sha256(payload).hexdigest()


def freeze_selection(dataset: Path, out_path: Path, n_per_label: int = 100) -> dict[str, Any]:
    data = json.loads(dataset.read_text(encoding='utf-8'))
    rng = random.Random(SEED)
    selected: list[dict[str, Any]] = []
    for label in ('Attack', 'Non-Attack'):
        candidates = [(i, r) for i, r in enumerate(data) if r.get('Label') == label]
        rng.shuffle(candidates)
        chosen: list[tuple[int, dict[str, Any]]] = []
        seen_rules: set[str] = set()
        # Maximize alert-rule diversity first, before filling randomly.
        for i, r in candidates:
            rule = str(r.get('rule_name', ''))
            if rule not in seen_rules:
                chosen.append((i, r)); seen_rules.add(rule)
                if len(chosen) == n_per_label: break
        if len(chosen) < n_per_label:
            chosen_idx = {i for i, _ in chosen}
            for i, r in candidates:
                if i in chosen_idx: continue
                chosen.append((i, r))
                if len(chosen) == n_per_label: break
        for i, r in chosen:
            selected.append({
                'index': i,
                'label': label,
                'rule_name': r.get('rule_name',''),
                'record_sha256': canon_hash(r),
            })
    frozen = {
        'dataset': str(dataset), 'seed': SEED, 'n_per_label': n_per_label,
        'selection_rule': 'shuffle within label; maximize unique rule_name before deterministic fill; freeze before model outputs',
        'fields_primary': ALL_FIELDS,
        'content_only_exclude': sorted(CONTENT_ONLY_EXCLUDE),
        'selected': selected,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(frozen, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    return frozen


def load_frozen(dataset: Path, frozen_path: Path) -> list[dict[str, Any]]:
    data = json.loads(dataset.read_text(encoding='utf-8'))
    frozen = json.loads(frozen_path.read_text(encoding='utf-8'))
    out=[]
    for s in frozen['selected']:
        r=data[s['index']]
        if canon_hash(r) != s['record_sha256'] or r['Label'] != s['label']:
            raise RuntimeError('Frozen SecAlertBench record mismatch')
        out.append({'index': s['index'], **r})
    return out


def visible_fields(record: dict[str, Any], view: str = 'primary') -> list[str]:
    fields=[f for f in ALL_FIELDS if record.get(f) not in ('', None, [], {})]
    if view == 'content_only':
        fields=[f for f in fields if f not in CONTENT_ONLY_EXCLUDE]
    return fields


def render(record: dict[str, Any], fields: list[str]) -> str:
    obj={k: record.get(k) for k in fields}
    return (
        'You are a Tier-1 security operations analyst. Review only the SOC alert evidence below. '
        'Decide whether the alert represents a real attack that requires escalation or a non-attack/false positive that can be closed. '
        'Return exactly ESCALATE or CLOSE and no explanation. Do not assume omitted fields are benign.\n\n'
        'ALERT EVIDENCE:\n' + json.dumps(obj, ensure_ascii=False, sort_keys=True)
    )


def norm(text: str) -> str:
    u=text.upper()
    if re.search(r'\bESCALATE\b',u): return 'ESCALATE'
    if re.search(r'\bCLOSE\b',u): return 'CLOSE'
    return 'UNPARSEABLE'


def expected(label: str) -> str:
    return 'ESCALATE' if label == 'Attack' else 'CLOSE'


def run_transformers(dataset: Path, frozen_path: Path, model_path: str, model_name: str, outdir: Path, batch_size: int = 4, view: str = 'primary') -> dict[str, Any]:
    import torch
    from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration
    torch.manual_seed(SEED)
    records=load_frozen(dataset,frozen_path)
    model=Qwen2_5_VLForConditionalGeneration.from_pretrained(model_path,torch_dtype=torch.bfloat16,device_map='auto')
    # Deterministic greedy decoding; clear sampling-only defaults saved with some checkpoints.
    model.generation_config.temperature = None
    model.generation_config.top_p = None
    model.generation_config.top_k = None
    processor=AutoProcessor.from_pretrained(model_path); processor.tokenizer.padding_side='left'

    full_jobs=[]
    for r in records:
        fs=visible_fields(r,view)
        full_jobs.append((r['index'],'full',None,render(r,fs)))

    def infer(jobs):
        outputs={}
        for start in range(0,len(jobs),batch_size):
            batch=jobs[start:start+batch_size]; texts=[]
            for *_,prompt in batch:
                msgs=[{'role':'user','content':[{'type':'text','text':prompt}]}]
                texts.append(processor.apply_chat_template(msgs,tokenize=False,add_generation_prompt=True))
            inp=processor(text=texts,padding=True,return_tensors='pt')
            inp={k:(v.to(model.device) if hasattr(v,'to') else v) for k,v in inp.items()}
            with torch.inference_mode(): gen=model.generate(**inp,max_new_tokens=10,do_sample=False)
            pre=inp['input_ids'].shape[1]
            dec=processor.batch_decode(gen[:,pre:],skip_special_tokens=True)
            for (idx,variant,omit,_),txt in zip(batch,dec): outputs[(idx,variant,omit)]=txt.strip()
        return outputs

    t0=time.time(); full_out=infer(full_jobs)
    prelim=[]; omission_jobs=[]
    for r in records:
        raw=full_out[(r['index'],'full',None)]; lab=norm(raw); exp=expected(r['Label'])
        row={'index':r['index'],'label':r['Label'],'rule_name':r.get('rule_name',''),'full_raw':raw,'full_label':lab,'full_correct':lab==exp,'fields':visible_fields(r,view)}
        prelim.append(row)
        if r['Label']=='Attack' and row['full_correct']:
            fs=row['fields']
            for f in fs:
                omission_jobs.append((r['index'],'omit1',f,render(r,[x for x in fs if x != f])))
    omit_out=infer(omission_jobs)

    rows=[]
    byidx={r['index']:r for r in records}
    for row in prelim:
        omissions=[]
        if row['label']=='Attack' and row['full_correct']:
            for f in row['fields']:
                raw=omit_out[(row['index'],'omit1',f)]; lab=norm(raw)
                omissions.append({'field':f,'raw':raw,'label':lab,'target_flip':lab=='CLOSE'})
        row['single_omissions']=omissions
        row['mdo1']=any(x['target_flip'] for x in omissions)
        row['decisive_fields']=[x['field'] for x in omissions if x['target_flip']]
        rows.append(row)

    outdir.mkdir(parents=True,exist_ok=True)
    trials=outdir/f'{model_name}_{view}_trials.jsonl'
    trials.write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in rows),encoding='utf-8')
    atk=[r for r in rows if r['label']=='Attack']; non=[r for r in rows if r['label']=='Non-Attack']
    comp_atk=[r for r in atk if r['full_correct']]
    summary={
        'dataset':'SecAlertBench','view':view,'model':model_name,'seed':SEED,
        'n_total':len(rows),'n_attack':len(atk),'n_non_attack':len(non),
        'attack_full_correct':len(comp_atk),'attack_full_tpr':len(comp_atk)/len(atk),
        'non_attack_full_correct':sum(r['full_correct'] for r in non),'non_attack_tnr':sum(r['full_correct'] for r in non)/len(non),
        'overall_full_accuracy':sum(r['full_correct'] for r in rows)/len(rows),
        'n_attack_mdo1':sum(r['mdo1'] for r in comp_atk),
        'mdo1_rate_cond_attack_full_correct':sum(r['mdo1'] for r in comp_atk)/len(comp_atk) if comp_atk else None,
        'n_omission_prompts':len(omission_jobs),'elapsed_seconds':time.time()-t0,
    }
    (outdir/f'{model_name}_{view}_summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(summary,indent=2,sort_keys=True))
    return summary


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--dataset',default='data/public/secalertbench/secalertbench.json')
    p.add_argument('--frozen',default='results/secalertbench/FROZEN_COHORT.json')
    p.add_argument('--freeze',action='store_true')
    p.add_argument('--n-per-label',type=int,default=100)
    p.add_argument('--model-path')
    p.add_argument('--model-name')
    p.add_argument('--batch-size',type=int,default=4)
    p.add_argument('--view',choices=['primary','content_only'],default='primary')
    p.add_argument('--out-dir',default='results/secalertbench')
    a=p.parse_args()
    dataset=Path(a.dataset); frozen=Path(a.frozen)
    if a.freeze:
        f=freeze_selection(dataset,frozen,a.n_per_label)
        print(json.dumps({k:v for k,v in f.items() if k!='selected'},indent=2,ensure_ascii=False))
    else:
        if not a.model_path or not a.model_name: raise SystemExit('--model-path and --model-name required unless --freeze')
        run_transformers(dataset,frozen,a.model_path,a.model_name,Path(a.out_dir),a.batch_size,a.view)
