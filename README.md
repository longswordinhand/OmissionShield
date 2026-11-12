# OmissionShield reproducibility bundle — 2026-11-10 Phase-2 revision

This clean bundle corresponds to `manuscript/OmissionShield_TDSC_REV_2026-11-10.tex` and its compiled PDF.

Contents:
- `src/`: project Python source at the audited revision, excluding caches.
- `tests/`: 29 regression tests.
- `results/`: frozen result artifacts, including Qwen3 trials, ECI trials, mechanism ablation, and the failed high-competence SecAlertBench replication.
- `revision_notes/`: model identity recovery, ECI recount, protocol differences, hardware/re-timing, reproduction instructions, safe rerun wrappers, and reference/provenance notes.
- `protocols/`: core theory/threat/novelty notes.
- `manuscript/`: revised TeX/PDF and the two figures actually included in that manuscript.

Raw external datasets are not redistributed here. `revision_notes/SECALERTBENCH_PROVENANCE.md` pins the SecAlertBench upstream commit and SHA-256. The upstream repository currently has no LICENSE file, so redistribution rights are not assumed.

Historical model identity limitations are documented in `revision_notes/MODEL_IDENTITY.md`; mutable historical tags are not retroactively treated as immutable model identities.

Absolute local paths in release copies are normalized to `<PROJECT_ROOT>` and `<LOCAL_MODEL_ROOT>`; scientific numeric values are unchanged.

Use `revision_notes/REPRODUCE.md` and the safe wrappers under `revision_notes/safe_eval/` for new runs. New runs should not target the frozen `results/` tree.

The manuscript copy is byte-identical to the locked Phase-2 revision. It intentionally retains the local model path disclosed in the paper because that path is part of the model-identity limitation record; other release-note copies normalize local filesystem paths where possible.

Security note: `src/composition_bench.py` contains `KEY = b"omissionshield-composition-benchmark-key"` as a deterministic, non-secret benchmark/demo constant used only to exercise HMAC behavior. It is not a credential or production key and must not be reused as one.
