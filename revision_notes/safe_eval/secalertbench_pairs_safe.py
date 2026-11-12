import argparse
from pathlib import Path
from _guard import guarded_out
from src.secalertbench_pairs import run_transformers, run_ollama
p=argparse.ArgumentParser(); p.add_argument('--dataset',default='data/public/secalertbench/secalertbench.json'); p.add_argument('--frozen',default='results/secalertbench/FROZEN_COHORT.json'); p.add_argument('--single-trials',required=True); p.add_argument('--model-name',required=True); p.add_argument('--model-path'); p.add_argument('--backend',choices=['transformers','ollama'],required=True); p.add_argument('--batch-size',type=int,default=4); p.add_argument('--view',default='primary'); p.add_argument('--out-dir',required=True); p.add_argument('--force',action='store_true'); a=p.parse_args(); out=guarded_out(a.out_dir,a.force)
if a.backend=='transformers':
    if not a.model_path: raise SystemExit('--model-path required for transformers')
    run_transformers(Path(a.dataset),Path(a.frozen),Path(a.single_trials),a.model_path,a.model_name,out,a.batch_size,a.view)
else: run_ollama(Path(a.dataset),Path(a.frozen),Path(a.single_trials),a.model_name,out,a.view)
