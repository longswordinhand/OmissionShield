import argparse
from _guard import guarded_out
from src.real_stats import run
p=argparse.ArgumentParser(); p.add_argument('--out-file',required=True); p.add_argument('--force',action='store_true'); a=p.parse_args(); run(guarded_out(a.out_file,a.force))
