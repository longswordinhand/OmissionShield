import argparse
from _guard import guarded_out
from src.phase0 import run
p=argparse.ArgumentParser(); p.add_argument('--out-dir',required=True); p.add_argument('--seed',type=int,default=20260824); p.add_argument('--force',action='store_true'); a=p.parse_args(); run(guarded_out(a.out_dir,a.force),a.seed)
