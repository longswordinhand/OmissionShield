import argparse
from _guard import guarded_out
import src.tqrg_holdout as m
p=argparse.ArgumentParser(); p.add_argument('--out-dir',required=True); p.add_argument('--force',action='store_true'); a=p.parse_args(); m.OUT=guarded_out(a.out_dir,a.force); m.freeze_and_fetch()
