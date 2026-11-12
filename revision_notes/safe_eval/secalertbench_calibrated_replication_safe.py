import argparse
from pathlib import Path
from _guard import guarded_out
from src.secalertbench_calibrated_replication import run
p=argparse.ArgumentParser(); p.add_argument('--dataset',default='data/public/secalertbench/secalertbench.json'); p.add_argument('--test-frozen',default='results/secalertbench/FROZEN_COHORT.json'); p.add_argument('--calibration',default='results/secalertbench_highcompetence/CALIBRATION_COHORT_FROZEN_2026-09-28.json'); p.add_argument('--model-path',required=True); p.add_argument('--model-name',required=True); p.add_argument('--out-dir',required=True); p.add_argument('--force',action='store_true'); a=p.parse_args(); run(Path(a.dataset),Path(a.test_frozen),Path(a.calibration),a.model_path,a.model_name,guarded_out(a.out_dir,a.force))
