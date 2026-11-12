import argparse
from pathlib import Path
from _guard import guarded_out
from src.secalertbench_ollama_eval import run
p=argparse.ArgumentParser(); p.add_argument('--dataset',default='data/public/secalertbench/secalertbench.json'); p.add_argument('--frozen',default='results/secalertbench/FROZEN_COHORT.json'); p.add_argument('--model-name',default='qwen3_8_2b_q4km'); p.add_argument('--view',choices=['primary','content_only'],default='primary'); p.add_argument('--out-dir',required=True); p.add_argument('--force',action='store_true'); a=p.parse_args(); run(Path(a.dataset),Path(a.frozen),guarded_out(a.out_dir,a.force),a.model_name,a.view)
