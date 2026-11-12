import argparse
from _guard import guarded_out
from src.phase1_multimodel import run_transformers
p=argparse.ArgumentParser(); p.add_argument('--model-path',required=True); p.add_argument('--model-name',required=True); p.add_argument('--batch-size',type=int,default=8); p.add_argument('--out-dir',required=True); p.add_argument('--force',action='store_true'); a=p.parse_args(); run_transformers(a.model_path,a.model_name,guarded_out(a.out_dir,a.force),a.batch_size)
