from __future__ import annotations
import json, statistics
from pathlib import Path


def load(path):
    return [json.loads(x) for x in Path(path).read_text().splitlines() if x.strip()]

commits=load('results/tqrg_real/commits.jsonl')+load('results/tqrg_holdout/commits.jsonl')
rows=[]
for c in commits:
    fs=[f for f in c['files'] if f.get('patch')]
    raw=sum(len((f.get('patch') or '').encode('utf-8')) for f in fs)
    # Flat coverage certificate baseline: canonical JSON list of source IDs only.
    source_ids=sorted(f['filename'] for f in c['files'])
    flat_manifest=len(json.dumps(source_ids,separators=(',',':')).encode('utf-8'))
    # Minimal compositional control-plane payload: source IDs plus one parent-edge encoding per ID.
    ids=sum(len(x.encode('utf-8')) for x in source_ids)
    edge_overhead=sum(len(x.encode('utf-8'))+8 for x in source_ids)
    control=ids+edge_overhead
    rows.append({'sha':c['sha'],'n_files':len(c['files']),'raw_patch_bytes':raw,'flat_manifest_bytes':flat_manifest,'control_plane_bytes':control,'ratio_raw_to_control':raw/control if control else None,'ratio_control_to_flat_manifest':control/flat_manifest if flat_manifest else None})
raws=[r['raw_patch_bytes'] for r in rows]; flats=[r['flat_manifest_bytes'] for r in rows]; ctrls=[r['control_plane_bytes'] for r in rows]; ratios=[r['ratio_raw_to_control'] for r in rows if r['ratio_raw_to_control'] is not None]; dag_flat=[r['ratio_control_to_flat_manifest'] for r in rows if r['ratio_control_to_flat_manifest'] is not None]
summary={
 'n_commits':len(rows),
 'definition':'raw textual patch UTF-8 bytes, canonical flat source-ID manifest bytes, and a minimal source-ID-plus-parent-edge encoding; excludes cryptographic signatures and implementation object overhead',
 'raw_patch_bytes_total':sum(raws),
 'flat_manifest_bytes_total':sum(flats),
 'control_plane_bytes_total':sum(ctrls),
 'aggregate_control_to_flat_manifest_ratio':sum(ctrls)/sum(flats),
 'aggregate_raw_to_control_ratio':sum(raws)/sum(ctrls),
 'median_per_commit_raw_patch_bytes':statistics.median(raws),
 'median_per_commit_flat_manifest_bytes':statistics.median(flats),
 'median_per_commit_control_plane_bytes':statistics.median(ctrls),
 'median_per_commit_raw_to_control_ratio':statistics.median(ratios),
 'median_per_commit_control_to_flat_manifest_ratio':statistics.median(dag_flat),
 'min_ratio':min(ratios),'max_ratio':max(ratios),
}
out=Path('results/control_plane_footprint');out.mkdir(exist_ok=True)
(out/'trials.jsonl').write_text(''.join(json.dumps(r,sort_keys=True)+'\n' for r in rows))
(out/'summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
print(json.dumps(summary,indent=2))
