import argparse
from _guard import guarded_out
from src.tqrg_real_bench import fetch_all
p=argparse.ArgumentParser(); p.add_argument('--out-dir',required=True); p.add_argument('--n',type=int,default=20); p.add_argument('--force',action='store_true'); a=p.parse_args(); fetch_all(guarded_out(a.out_dir,a.force),a.n)
