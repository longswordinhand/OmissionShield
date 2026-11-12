import argparse
from pathlib import Path
from _guard import guarded_out
from src.tqrg_transformers_pairs import run
p=argparse.ArgumentParser(); p.add_argument('--model-path',required=True); p.add_argument('--model-name',required=True); p.add_argument('--batch-size',type=int,default=2); p.add_argument('--out-dir',required=True); p.add_argument('--force',action='store_true'); a=p.parse_args(); run(a.model_path,a.model_name,guarded_out(a.out_dir,a.force),a.batch_size)
