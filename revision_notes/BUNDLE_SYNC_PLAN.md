# Reproducibility bundle sync plan — DO NOT APPLY YET

Bundle compared:
`submission/tdsc_agentic_si_2027/artifact/OmissionShield_reproducibility/`

Comparison method: `diff -rq` between project `src/` and bundle `src/`, and project `results/` and bundle `results/`. This file records the verified delta only; no bundle file was modified.

## Missing source files

Present in project `src/` but absent from bundle `src/`:
- `make_fig1_novelty.py`
- `secalertbench_calibrated_replication.py`
- `secalertbench_causal_eval.py`

Bundle also contains stale/different `__pycache__` files; the resynced bundle should exclude all `__pycache__/` and `.pyc` files rather than sync them.

## Missing result trees/files

Present in project but absent from bundle at the corresponding path:
- `results/_inventory/` (including `RESULTS_INDEX.md`)
- `results/mechanism_ablation/` (bundle has only a root-level summary copy; project trials are missing)
- `results/secalertbench/eci/`
- `results/secalertbench/PAIR_FOLLOWUP_PROTOCOL.md`
- `results/secalertbench_highcompetence/` (including failed Qwen3-30B replication protocol/results)
- `results/tqrg_holdout/eci/`
- `results/tqrg_holdout/llm_qwen3/`
- `results/tqrg_real/eci/`
- `results/tqrg_real/llm_qwen3/`
- `results/tqrg_combined_stats.json` at the expected bundle path

## Path mismatch

The bundle contains an extra nested `results/results/` directory. The combined stats file is nested there, while provenance cites `results/tqrg_combined_stats.json`. The approved sync should place it at the provenance path and eliminate the accidental extra nesting.

## Files that differ rather than being absent

- `results/control_plane_footprint/trials.jsonl`: bundle copy strips fields present in project rows; needs an explicit decision whether bundle should be byte-identical to source-of-truth or intentionally redacted, with documentation.
- `results/phase1_multimodel/qwen2_5_vl_3b_summary.json`
- `results/phase1_multimodel/qwen2_5_vl_7b_summary.json`
  Project versions contain absolute local model paths; bundle versions rewrite them. Any redaction/normalization must be documented rather than silent.

## Stale zip and checksums

- `submission/tdsc_agentic_si_2027/artifact/OmissionShield_reproducibility_submission_snapshot.zip` timestamp: 2026-08-25 17:09; it predates the Sep-28 bundle state and is stale.
- `OmissionShield_reproducibility/SHA256SUMS.txt` is also timestamped 2026-08-25 and does not cover all later bundle content.

After Muse approval only:
1. build a clean new bundle from an explicit inclusion manifest;
2. exclude caches/local secrets/absolute paths;
3. include verified missing trial artifacts and protocols;
4. repair path nesting;
5. generate checksums for every released file;
6. generate a new zip from that exact checked directory;
7. verify zip extraction against the manifest and checksums;
8. mark the Aug-25 zip superseded or remove it from the submission package.

## External raw data

The project-only raw datasets are not blindly copied into the bundle. Instead, release planning should pin upstream provenance and hashes and determine license-compatible redistribution. SecAlertBench currently has no LICENSE file upstream; therefore redistribution rights must not be assumed.

## Availability status

No real public code/archive destination is approved yet. The manuscript availability paragraph must say so until a real repository/DOI is created.
