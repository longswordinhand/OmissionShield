import argparse
from pathlib import Path
from _guard import guarded_out
from src.tqrg_llm_eval import run
p=argparse.ArgumentParser(); p.add_argument('--input',required=True); p.add_argument('--out-dir',required=True); p.add_argument('--max-k',type=int,default=2); p.add_argument('--force',action='store_true'); a=p.parse_args(); run(Path(a.input),guarded_out(a.out_dir,a.force),a.max_k)
