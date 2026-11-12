from __future__ import annotations
import argparse, hashlib, json, math, time
from pathlib import Path
from typing import Any
from src.secalertbench_eval import load_frozen, visible_fields, render, SEED

def canon_hash(record: dict[str, Any]) -> str:
    payload=json.dumps(record,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')
    return hashlib.sha256(payload).hexdigest()

def load_calibration(dataset: Path, calibration_path: Path) -> list[dict[str, Any]]:
    data=json.loads(dataset.read_text(encoding='utf-8'))
    frozen=json.loads(calibration_path.read_text(encoding='utf-8'))
    out=[]
    for s in frozen['selected']:
        r=data[s['index']]
        if r.get('Label') != s['label'] or canon_hash(r) != s['record_sha256']:
            raise RuntimeError(f"Calibration record mismatch at index {s['index']}")
        out.append({'index':s['index'], **r})
    return out

def choose_threshold(rows: list[dict[str, Any]]) -> dict[str, Any]:
    scores=sorted(set(float(r['score']) for r in rows))
    if not scores:
        raise RuntimeError('No calibration scores')
    eps=max(1e-6,(scores[-1]-scores[0]+1.0)*1e-9)
    candidates=[scores[0]-eps]
    candidates += [(a+b)/2.0 for a,b in zip(scores,scores[1:])]
    candidates += [scores[-1]+eps]
    n_a=sum(r['label']=='Attack' for r in rows)
    n_n=sum(r['label']=='Non-Attack' for r in rows)
    evals=[]
    for t in candidates:
        tp=sum(r['label']=='Attack' and r['score']>=t for r in rows)
        tn=sum(r['label']=='Non-Attack' and r['score']<t for r in rows)
        tpr=tp/n_a; tnr=tn/n_n; bal=(tpr+tnr)/2
        evals.append({'threshold':t,'attack_tpr':tpr,'nonattack_tnr':tnr,
                      'balanced_accuracy':bal,'min_class_rate':min(tpr,tnr)})
    best=max(evals,key=lambda x:(x['balanced_accuracy'],x['min_class_rate'],-abs(x['threshold']),-x['threshold']))
    return {'selected':best,'n_candidates':len(candidates)}

def run(dataset: Path, test_frozen: Path, calibration_path: Path, model_path: str,
        model_name: str, outdir: Path):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    torch.manual_seed(SEED)
    calibration=load_calibration(dataset,calibration_path)
    test=load_frozen(dataset,test_frozen)

    tokenizer=AutoTokenizer.from_pretrained(model_path,local_files_only=True)
    esc_ids=tokenizer.encode('ESCALATE',add_special_tokens=False)
    close_ids=tokenizer.encode('CLOSE',add_special_tokens=False)
    if not esc_ids or not close_ids:
        raise RuntimeError('Target label tokenization failed')
    esc_id=esc_ids[0]; close_id=close_ids[0]
    print(json.dumps({'esc_ids':esc_ids,'close_ids':close_ids,'esc_first':esc_id,'close_first':close_id}),flush=True)

    model=AutoModelForCausalLM.from_pretrained(
        model_path,device_map='auto',torch_dtype='auto',local_files_only=True
    )
    model.eval()

    counter=0
    def score_prompt(prompt: str) -> float:
        nonlocal counter
        msgs=[{'role':'user','content':prompt}]
        inp=tokenizer.apply_chat_template(
            msgs,add_generation_prompt=True,tokenize=True,return_dict=True,return_tensors='pt'
        )
        inp={k:v.to(model.device) for k,v in inp.items()}
        with torch.inference_mode():
            logits=model(**inp,use_cache=False).logits[0,-1]
        a=float(logits[esc_id].float().item())
        c=float(logits[close_id].float().item())
        s=a-c
        if not (math.isfinite(a) and math.isfinite(c) and math.isfinite(s)):
            raise RuntimeError(f'Non-finite score: ESC={a} CLOSE={c}')
        counter+=1
        if counter % 25 == 0:
            print(f'[score {counter}] delta={s:.6f}',flush=True)
        return s

    t0=time.time()
    cal_rows=[]
    for r in calibration:
        fs=visible_fields(r,'primary')
        cal_rows.append({'index':r['index'],'label':r['Label'],'rule_name':r.get('rule_name',''),
                         'score':score_prompt(render(r,fs)),'fields':fs})
    threshold_info=choose_threshold(cal_rows)
    tau=float(threshold_info['selected']['threshold'])
    print('CALIBRATION',json.dumps(threshold_info,sort_keys=True),flush=True)

    test_rows=[]
    for r in test:
        fs=visible_fields(r,'primary')
        s=score_prompt(render(r,fs))
        pred='ESCALATE' if s>=tau else 'CLOSE'
        correct=(pred==('ESCALATE' if r['Label']=='Attack' else 'CLOSE'))
        test_rows.append({'index':r['index'],'label':r['Label'],'rule_name':r.get('rule_name',''),
                          'score':s,'prediction':pred,'full_correct':correct,'fields':fs})

    atk=[r for r in test_rows if r['label']=='Attack']; non=[r for r in test_rows if r['label']=='Non-Attack']
    tpr=sum(r['prediction']=='ESCALATE' for r in atk)/len(atk)
    tnr=sum(r['prediction']=='CLOSE' for r in non)/len(non)
    bal=(tpr+tnr)/2
    gate=(tpr>=0.70 and tnr>=0.70 and bal>=0.75)
    full_summary={'model':model_name,'threshold':tau,'score_definition':'next-token logit(ESCALATE first token)-logit(CLOSE token)',
                  'attack_tpr':tpr,'nonattack_tnr':tnr,'balanced_accuracy':bal,
                  'attack_full_correct':sum(r['full_correct'] for r in atk),
                  'nonattack_full_correct':sum(r['full_correct'] for r in non),
                  'competence_gate_pass':gate,'n_test':len(test_rows),'elapsed_seconds_to_full':time.time()-t0}
    print('FULL',json.dumps(full_summary,sort_keys=True),flush=True)

    outdir.mkdir(parents=True,exist_ok=True)
    (outdir/f'{model_name}_calibration_scores.jsonl').write_text(
        ''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in cal_rows),encoding='utf-8')
    (outdir/f'{model_name}_threshold.json').write_text(
        json.dumps(threshold_info,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    (outdir/f'{model_name}_test_full_scores.jsonl').write_text(
        ''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in test_rows),encoding='utf-8')
    (outdir/f'{model_name}_test_full_summary.json').write_text(
        json.dumps(full_summary,indent=2,sort_keys=True)+'\n',encoding='utf-8')

    if not gate:
        print('COMPETENCE_GATE_FAIL; stopping before SES interventions',flush=True)
        return

    records={r['index']:r for r in test}
    comp=[r for r in test_rows if r['label']=='Attack' and r['full_correct']]
    ses_rows=[]
    for j,row in enumerate(comp,1):
        rec=records[row['index']]
        omissions=[]
        for f in row['fields']:
            kept=[x for x in row['fields'] if x!=f]
            s=score_prompt(render(rec,kept))
            pred='ESCALATE' if s>=tau else 'CLOSE'
            omissions.append({'field':f,'score':s,'prediction':pred,'target_flip':pred=='CLOSE'})
        ses_rows.append({**row,'single_omissions':omissions,
                         'mdo1':any(x['target_flip'] for x in omissions),
                         'decisive_fields':[x['field'] for x in omissions if x['target_flip']]})
        print(f'[SES {j}/{len(comp)}] idx={row["index"]} mdo1={ses_rows[-1]["mdo1"]}',flush=True)

    n_mdo1=sum(r['mdo1'] for r in ses_rows)
    ses_summary={'model':model_name,'threshold':tau,
                 'attack_full_correct':len(comp),'n_attack_mdo1':n_mdo1,
                 'mdo1_rate_cond_attack_full_correct':n_mdo1/len(comp) if comp else None,
                 'unconditional_attack_induced_fn_rate':n_mdo1/100.0,
                 'attack_tpr':tpr,'nonattack_tnr':tnr,'balanced_accuracy':bal,
                 'n_single_omission_prompts':sum(len(r['single_omissions']) for r in ses_rows),
                 'elapsed_seconds_total':time.time()-t0}
    (outdir/f'{model_name}_ses_single_trials.jsonl').write_text(
        ''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in ses_rows),encoding='utf-8')
    (outdir/f'{model_name}_ses_single_summary.json').write_text(
        json.dumps(ses_summary,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print('SES',json.dumps(ses_summary,sort_keys=True),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--dataset',default='data/public/secalertbench/secalertbench.json')
    p.add_argument('--test-frozen',default='results/secalertbench/FROZEN_COHORT.json')
    p.add_argument('--calibration',default='results/secalertbench_highcompetence/CALIBRATION_COHORT_FROZEN_2026-09-28.json')
    p.add_argument('--model-path',required=True);p.add_argument('--model-name',required=True)
    p.add_argument('--out-dir',default='results/secalertbench_highcompetence')
    a=p.parse_args()
    run(Path(a.dataset),Path(a.test_frozen),Path(a.calibration),a.model_path,a.model_name,Path(a.out_dir))
