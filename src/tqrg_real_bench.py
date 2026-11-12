from __future__ import annotations

import ast
import csv
import json
import random
import re
import urllib.request
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

CSV_PATH = Path('data/public/tqrg_security_patches.csv')
SEED = 20260824

@dataclass(frozen=True)
class Candidate:
    cve_id: str
    cwe_id: str
    project: str
    sha: str
    commit_url: str
    language: str
    n_files: int
    total_changes: int
    file_names: tuple[str, ...]


def _parse_files(value: str) -> dict[str, dict[str, Any]]:
    try:
        x=ast.literal_eval(value)
        return x if isinstance(x,dict) else {}
    except Exception:
        return {}


def select_candidates(n: int=20) -> list[Candidate]:
    pool=[]
    with CSV_PATH.open(newline='',encoding='utf-8',errors='replace') as f:
        for row in csv.DictReader(f):
            cve=(row.get('cve_id') or '').strip()
            project=(row.get('project') or '').strip().rstrip('/')
            sha=(row.get('sha') or '').strip()
            if not cve.startswith('CVE-') or not project.startswith('https://github.com/') or not re.fullmatch(r'[0-9a-fA-F]{7,40}',sha):
                continue
            files=_parse_files(row.get('files') or '')
            if not (2 <= len(files) <= 5):
                continue
            total=sum(int(v.get('changes') or 0) for v in files.values())
            if not (4 <= total <= 180):
                continue
            # At least one source-like extension; avoid commits consisting solely of docs/data.
            code_ext={'.c','.h','.cc','.cpp','.py','.php','.java','.js','.ts','.go','.rb','.rs','.m','.cs'}
            if not any(Path(name).suffix.lower() in code_ext for name in files):
                continue
            owner_repo=project.removeprefix('https://github.com/')
            commit_url=f'https://api.github.com/repos/{owner_repo}/commits/{sha}'
            pool.append(Candidate(cve,row.get('cwe_id',''),project,sha,commit_url,row.get('language',''),len(files),total,tuple(files.keys())))
    # Deterministic project-stratified sample so one large project cannot dominate.
    rng=random.Random(SEED)
    rng.shuffle(pool)
    chosen=[]; projects=set(); cves=set()
    for c in pool:
        if c.project in projects or c.cve_id in cves:
            continue
        chosen.append(c); projects.add(c.project); cves.add(c.cve_id)
        if len(chosen)>=n: break
    return chosen


def preregister(out: Path, n: int=20) -> list[Candidate]:
    out.mkdir(parents=True,exist_ok=True)
    chosen=select_candidates(n)
    obj={
        'seed':SEED,
        'selection_before_patch_retrieval':True,
        'criteria':{
            'CVE_id_required':True,
            'github_project_required':True,
            'changed_files_range':[2,5],
            'total_changes_range':[4,180],
            'at_least_one_source_extension':True,
            'unique_project':True,
            'unique_CVE':True,
        },
        'planned_n':n,
        'selected_n':len(chosen),
        'candidates':[asdict(c) for c in chosen],
        'post_selection_exclusions_allowed':['GitHub API inaccessible','commit no longer exists','no textual patch returned for any changed file'],
    }
    (out/'preregistered_candidates.json').write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')
    return chosen


def fetch_commit(c: Candidate) -> dict[str,Any]:
    req=urllib.request.Request(c.commit_url,headers={'Accept':'application/vnd.github+json','User-Agent':'OmissionShield-research'})
    with urllib.request.urlopen(req,timeout=30) as r:
        d=json.load(r)
    files=[]
    for f in d.get('files',[]):
        files.append({
            'filename':f.get('filename'),
            'status':f.get('status'),
            'additions':f.get('additions'),
            'deletions':f.get('deletions'),
            'changes':f.get('changes'),
            'patch':f.get('patch'),
        })
    return {
        'cve_id':c.cve_id,'cwe_id':c.cwe_id,'project':c.project,'sha':c.sha,
        'html_url':d.get('html_url'),'message':((d.get('commit') or {}).get('message') or ''),
        'files':files,
    }


def fetch_all(out: Path, n:int=20) -> dict[str,Any]:
    chosen=preregister(out,n)
    rows=[]; errors=[]
    for c in chosen:
        try:
            d=fetch_commit(c)
            if not any(f.get('patch') for f in d['files']):
                errors.append({'sha':c.sha,'reason':'no textual patch'})
                continue
            rows.append(d)
        except Exception as e:
            errors.append({'sha':c.sha,'reason':f'{type(e).__name__}: {e}'})
    with (out/'commits.jsonl').open('w',encoding='utf-8') as f:
        for r in rows: f.write(json.dumps(r,sort_keys=True)+'\n')
    summary={'selected':len(chosen),'retrieved':len(rows),'excluded':len(errors),'errors':errors}
    (out/'fetch_summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
    print(json.dumps(summary,indent=2,sort_keys=True))
    return summary

if __name__=='__main__':
    fetch_all(Path('results/tqrg_real'),20)
