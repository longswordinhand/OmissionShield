import argparse
from _guard import guarded_out
from src.benchmark_overhead import run
p=argparse.ArgumentParser(); p.add_argument('--out-dir',required=True); p.add_argument('--force',action='store_true'); a=p.parse_args(); run(guarded_out(a.out_dir,a.force))
