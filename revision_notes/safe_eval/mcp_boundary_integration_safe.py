import argparse
from _guard import guarded_out
from src.mcp_boundary_integration import benchmark
p=argparse.ArgumentParser(); p.add_argument('--out-dir',required=True); p.add_argument('--repeats',type=int,default=200); p.add_argument('--force',action='store_true'); a=p.parse_args(); benchmark(guarded_out(a.out_dir,a.force),a.repeats)
