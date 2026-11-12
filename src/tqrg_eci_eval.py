from __future__ import annotations
import json
from pathlib import Path
from src.runtime import TrustedEvidenceRuntime


def run(infile: Path, outdir: Path) -> dict:
    commits=[json.loads(x) for x in infile.read_text(encoding='utf-8').splitlines() if x.strip()]
    rows=[]
    for c in commits:
        files=[f for f in c['files'] if f.get('filename')]
        items=[(f['filename'], f.get('patch') or f"<non-textual:{f.get('status')}>") for f in files]
        # Complete execution
        rt=TrustedEvidenceRuntime(b'tqrg-eval-key')
        signed=rt.enumerate_source(c['sha'],items)
        ids=[x[0] for x in items]
        rt.deliver('collector',ids); rt.commit_derived('collector','terminal','review context')
        full=rt.gate(signed,['terminal'])
        rows.append({'cve_id':c['cve_id'],'sha':c['sha'],'variant':'complete','omitted':None,'allow':full.allow,'missing':sorted(full.missing_ids)})
        # Every single-file structural suppression
        for omit in ids:
            rt=TrustedEvidenceRuntime(b'tqrg-eval-key')
            signed=rt.enumerate_source(c['sha'],items)
            delivered=[x for x in ids if x!=omit]
            rt.deliver('collector',delivered); rt.commit_derived('collector','terminal','review context')
            dec=rt.gate(signed,['terminal'])
            rows.append({'cve_id':c['cve_id'],'sha':c['sha'],'variant':'suppress1','omitted':omit,'allow':dec.allow,'missing':sorted(dec.missing_ids)})
    outdir.mkdir(parents=True,exist_ok=True)
    with (outdir/'trials.jsonl').open('w',encoding='utf-8') as f:
        for r in rows:f.write(json.dumps(r,sort_keys=True)+'\n')
    complete=[r for r in rows if r['variant']=='complete']
    attack=[r for r in rows if r['variant']=='suppress1']
    summary={
      'n_commits':len(commits),'n_complete':len(complete),'n_single_file_suppressions':len(attack),
      'complete_accept_rate':sum(r['allow'] for r in complete)/len(complete),
      'suppression_detection_rate':sum(not r['allow'] for r in attack)/len(attack),
      'exact_missing_id_rate':sum(r['missing']==[r['omitted']] for r in attack)/len(attack),
    }
    (outdir/'summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
    print(json.dumps(summary,indent=2,sort_keys=True))
    return summary

if __name__=='__main__':
    run(Path('results/tqrg_real/commits.jsonl'),Path('results/tqrg_real/eci'))
