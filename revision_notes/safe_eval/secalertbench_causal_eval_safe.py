import argparse
from pathlib import Path
from _guard import guarded_out
from src.secalertbench_causal_eval import run
p=argparse.ArgumentParser(); p.add_argument('--dataset',default='data/public/secalertbench/secalertbench.json'); p.add_argument('--frozen',default='results/secalertbench/FROZEN_COHORT.json'); p.add_argument('--model-path',required=True); p.add_argument('--model-name',required=True); p.add_argument('--out-dir',required=True); p.add_argument('--batch-size',type=int,default=8); p.add_argument('--view',choices=['primary','content_only'],default='primary'); p.add_argument('--max-per-label',type=int); p.add_argument('--omissions',action='store_true'); p.add_argument('--force',action='store_true'); a=p.parse_args(); run(Path(a.dataset),Path(a.frozen),a.model_path,a.model_name,guarded_out(a.out_dir,a.force),a.batch_size,a.view,a.max_per_label,a.omissions)
