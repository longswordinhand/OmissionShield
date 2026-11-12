# OmissionShield Phase-1 reproduction guide (draft)

Run from the project root `/home/yguo56/projects/OmissionShield` unless stated otherwise. Do not use the original eval scripts' default output directories when reproducing frozen LLM experiments; direct any new output to a new directory under `revision_2026-11-10/` or `/tmp`.

## 1. Environment

```bash
python3 --version
python3 -m pip install -r revision_2026-11-10/requirements.txt
python3 -m pytest tests/ -q -p no:cacheprovider
```

Expected current test result on UISAI1: `29 passed`.

Environment used for Phase-1 re-timing is in `revision_2026-11-10/HARDWARE.md`.

## 2. Frozen input integrity

```bash
sha256sum data/public/secalertbench/secalertbench.json
cat data/public/secalertbench/SHA256SUMS.txt
```

Expected SecAlertBench SHA-256: `33f95305d1c42f8e615e4f94066119570859dee7eb086dff7c2273536c932ea3`.

Frozen Git cohorts are:
- `results/tqrg_real/commits.jsonl`
- `results/tqrg_holdout/commits.jsonl`
- `results/tqrg_holdout/FROZEN_COHORT_B.json`

Frozen SOC cohort:
- `results/secalertbench/FROZEN_COHORT.json`

## 3. Structural-count verification

The Phase-1 recount is documented in `revision_2026-11-10/ECI_3747_RECOUNT.md`. It reads frozen inputs only. The defensible present-evidence-removal count is 3,328; 419 additional SOC schema checks omit already-absent fields.

## 4. Model identity

Use `revision_2026-11-10/MODEL_IDENTITY.md` before attempting any LLM rerun. Historical 7B/3B TQRG `--model-path` and the historical Ollama digest were not logged, so exact historical LLM reproduction is not currently guaranteed.

Do not treat a present-day mutable tag as proof of a historical model artifact.

## 5. LLM experiment entry points (new output only)

Git Qwen3 entry point: `src/tqrg_llm_eval.py`; it has a hardcoded default output under `results/` and therefore must be copied/adapted before any rerun. Phase 1 did **not** rerun it.

Git Qwen2.5-VL single-removal evaluation:
```bash
python3 src/tqrg_transformers_eval.py --model-path <PINNED_LOCAL_PATH> --model-name <NAME> --batch-size 2 --out-dir revision_2026-11-10/reruns/tqrg_crossmodel
```

SecAlertBench Qwen2.5-VL evaluation:
```bash
python3 src/secalertbench_eval.py --dataset data/public/secalertbench/secalertbench.json --frozen results/secalertbench/FROZEN_COHORT.json --model-path <PINNED_LOCAL_PATH> --model-name <NAME> --batch-size 4 --out-dir revision_2026-11-10/reruns/secalertbench
```

These are potentially long GPU jobs. Their exact runtime depends on model/hardware; historical summaries record generation elapsed time but not a fully pinned environment, so no unsupported runtime promise is given here.

## 6. Overhead re-timing

```bash
PYTHONPATH=. python3 revision_2026-11-10/benchmark_overhead_retimed.py
```

Outputs:
- `revision_2026-11-10/overhead_retimed/timings.csv`
- `revision_2026-11-10/overhead_retimed/summary.json`

This uses `TrustedEvidenceRuntime.gate()` and therefore includes HMAC obligation verification. Commitment construction is repeated 100 times per size. Runtime is seconds to low minutes on UISAI1.

## 7. Table / figure provenance map (current)

- Git Qwen3 headline numbers: `results/tqrg_real/llm_qwen3/trials.jsonl` + `results/tqrg_holdout/llm_qwen3/trials.jsonl` -> `src/real_stats.py` -> manuscript Git results / Fig. 2 inputs.
- Git Qwen2.5-VL: `results/tqrg_crossmodel/qwen2_5_vl_7b_trials.jsonl` + `qwen2_5_vl_7b_mdo2_trials.jsonl` -> crossmodel summaries -> manuscript Git replication / Fig. 2.
- SOC primary: `results/secalertbench/qwen2_5_vl_7b_primary_trials.jsonl` + pair follow-up -> SOC tables.
- ECI Git: `results/tqrg_real/eci/trials.jsonl` + `results/tqrg_holdout/eci/trials.jsonl`.
- ECI SOC: `results/secalertbench/eci/trials.jsonl`; interpret with `ECI_3747_RECOUNT.md`.
- Composition: `results/composition/trials.jsonl` + `summary.json`.
- Mechanism ablation: `results/mechanism_ablation/trials.jsonl` + `summary.json`.
- Fig. 1 generator: `src/make_fig1_novelty.py`.
- Fig. 2 generator: `src/make_paper_figures.py`; currently assumes project-root paths and writes to `paper/figures/`.

## 8. Availability draft

There is **no approved public code/archive URL yet**. Do not claim one exists.

Draft manuscript paragraph:

> **Data and code availability.** The study uses two public-source datasets/artifacts: the TQRG security-patch dataset and the SecAlertBench public artifact, with frozen cohorts and cryptographic hashes recorded in the reproducibility package. The OmissionShield source code, frozen experiment configurations, per-case result artifacts, and scripts required to regenerate the reported non-LLM analyses will be deposited in an archival public repository upon approval of the final release package. No public archival URL has been assigned as of 10 November 2026; the final manuscript must not cite a repository or DOI until one actually exists.

Muse should decide the real release destination and timing before Phase 2/final submission.

## 9. Safe rerun entry points

Phase 2 adds wrappers under `revision_2026-11-10/safe_eval/`. These wrappers require an explicit `--out-dir` and refuse any destination under the frozen project `results/` tree unless `--force` is explicitly supplied. New reproducibility runs should use these wrappers rather than the historical entry points with unsafe defaults.

Examples:

```bash
PYTHONPATH=.:revision_2026-11-10/safe_eval python3 revision_2026-11-10/safe_eval/tqrg_transformers_eval_safe.py \
  --model-path <PINNED_LOCAL_PATH> --model-name <NAME> --batch-size 2 \
  --out-dir revision_2026-11-10/reruns/tqrg_crossmodel

PYTHONPATH=.:revision_2026-11-10/safe_eval python3 revision_2026-11-10/safe_eval/tqrg_llm_eval_safe.py \
  --input results/tqrg_real/commits.jsonl \
  --out-dir revision_2026-11-10/reruns/tqrg_qwen3
```

The `--force` option exists only for an explicitly approved future maintenance action; it should not be used for normal reproduction.

## 10. Phase-2 fix-round result-writing guard audit

A full scan of `src/*.py` for references to `results/` found 25 scripts. Every script that can write into the frozen `results/` tree now has a corresponding wrapper under `revision_2026-11-10/safe_eval/`. The wrappers require an explicit output path and pass it through `_guard.guarded_out()`, which refuses any path at or below `<PROJECT_ROOT>/results` unless `--force` is explicitly supplied.

Safe wrappers now cover:

- `benchmark_overhead.py`
- `composition_bench.py`
- `controlled_bench.py`
- `control_plane_footprint.py`
- `end_to_end.py`
- `mcp_boundary_integration.py`
- `mechanism_ablation.py`
- `phase0.py`
- `phase0c_llm.py`
- `phase1_multimodel.py`
- `real_stats.py`
- `secalertbench_calibrated_replication.py`
- `secalertbench_causal_eval.py`
- `secalertbench_eci_eval.py`
- `secalertbench_eval.py`
- `secalertbench_ollama_eval.py`
- `secalertbench_pairs.py`
- `secalertbench_stats.py`
- `tqrg_eci_eval.py`
- `tqrg_holdout.py`
- `tqrg_llm_eval.py`
- `tqrg_real_bench.py`
- `tqrg_transformers_eval.py`
- `tqrg_transformers_pairs.py`

`make_paper_figures.py` is the one `results/`-referencing script without a frozen-results guard because it is a **reader of `results/`**, not a writer to that tree; its outputs are figures under `paper/figures/`. It is therefore outside the M-20 frozen-results overwrite threat. It should still be run only when intentionally regenerating paper figures.

The wrappers for `control_plane_footprint.py` and `secalertbench_stats.py` reproduce their small analysis logic locally because those historical scripts execute or hard-code result output paths in a way that makes safe importing unsuitable. No file under `src/` was modified.

After these wrapper additions, all wrapper files passed `python3 -m py_compile`, and the project test suite passed 29/29.
