from __future__ import annotations

from itertools import combinations
import json
from pathlib import Path
import re
from typing import Any

from src.phase0c_llm import call_ollama


def load_commits(path: Path) -> list[dict[str,Any]]:
    return [json.loads(x) for x in path.read_text(encoding='utf-8').splitlines() if x.strip()]


def textual_files(commit: dict[str,Any]) -> list[dict[str,Any]]:
    return [f for f in commit['files'] if f.get('patch')]


def render(files: list[dict[str,Any]]) -> str:
    chunks=[]
    for i,f in enumerate(files,1):
        patch=f.get('patch') or ''
        chunks.append(f"FILE {i}: {f['filename']}\nPATCH:\n{patch}")
    return (
        "/no_think\nYou are reviewing a software commit using only the changed-file patches below. "
        "Decide whether the patch contains a security-relevant vulnerability fix (for example memory safety, "
        "authentication/authorization, injection, cryptographic validation, information disclosure, denial of service caused by unsafe input handling, or another security flaw). "
        "Do not infer from a CVE identifier or commit metadata because none is provided. "
        "Return exactly SECURITY_FIX or NO_SECURITY_FIX and no explanation.\n\n" + "\n\n".join(chunks)
    )


def norm(text:str)->str:
    up=text.upper()
    if re.search(r'\bNO_SECURITY_FIX\b',up): return 'NO_SECURITY_FIX'
    if re.search(r'\bSECURITY_FIX\b',up): return 'SECURITY_FIX'
    return 'UNPARSEABLE'


def eval_commit(c:dict[str,Any], max_k:int=2)->dict[str,Any]:
    files=textual_files(c)
    full_raw=call_ollama(render(files)); full=norm(full_raw)
    row={
        'cve_id':c['cve_id'],'project':c['project'],'sha':c['sha'],
        'n_changed_files':len(c['files']),'n_textual_files':len(files),
        'file_names':[f['filename'] for f in files],
        'full_raw':full_raw,'full_label':full,'full_correct':full=='SECURITY_FIX',
        'mdo_leq2':None,'decisive_omissions':[], 'evaluated_subsets':0,
    }
    if full!='SECURITY_FIX' or len(files)<2:
        return row
    indices=range(len(files))
    for k in range(1,min(max_k,len(files)-1)+1):
        wins=[]
        for omit in combinations(indices,k):
            kept=[f for j,f in enumerate(files) if j not in omit]
            raw=call_ollama(render(kept)); lab=norm(raw)
            row['evaluated_subsets']+=1
            if lab=='NO_SECURITY_FIX':
                wins.append({'k':k,'omitted_indices':list(omit),'omitted_files':[files[j]['filename'] for j in omit],'raw':raw})
        if wins:
            row['mdo_leq2']=k
            row['decisive_omissions']=wins
            break
    return row


def run(infile:Path,outdir:Path,max_k:int=2)->dict[str,Any]:
    outdir.mkdir(parents=True,exist_ok=True)
    commits=load_commits(infile)
    rows=[]
    for i,c in enumerate(commits,1):
        r=eval_commit(c,max_k=max_k); rows.append(r)
        print(f"[{i}/{len(commits)}] {r['cve_id']} full={r['full_label']} mdo={r['mdo_leq2']} subsets={r['evaluated_subsets']}",flush=True)
    with (outdir/'trials.jsonl').open('w',encoding='utf-8') as f:
        for r in rows: f.write(json.dumps(r,sort_keys=True)+'\n')
    competent=[r for r in rows if r['full_correct']]
    vulnerable=[r for r in competent if r['mdo_leq2'] is not None]
    summary={
        'n_retrieved_commits':len(rows),
        'full_security_fix_recognition':sum(r['full_correct'] for r in rows)/len(rows) if rows else None,
        'n_full_correct':len(competent),
        'n_mdo1':sum(r['mdo_leq2']==1 for r in competent),
        'n_mdo2':sum(r['mdo_leq2']==2 for r in competent),
        'n_no_flip_within_2':sum(r['mdo_leq2'] is None for r in competent),
        'vulnerable_within_2_rate_cond_full_correct':len(vulnerable)/len(competent) if competent else None,
        'model':'qwen3:latest via Ollama, temperature=0, /no_think',
        'max_omission_budget':max_k,
    }
    (outdir/'summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(summary,indent=2,sort_keys=True))
    return summary

if __name__=='__main__':
    run(Path('results/tqrg_real/commits.jsonl'),Path('results/tqrg_real/llm_qwen3'),2)
