# Phase-1 overhead re-timing

This re-run measures `TrustedEvidenceRuntime.gate()` rather than raw `why_not_gate`, so each gate measurement includes `verify_obligation()` and its HMAC-SHA256 recomputation.

Sizes and gate repeats match the original scaling benchmark: 10/2000, 100/1000, 1000/300, 10000/50. Coverage-obligation commitment construction is repeated 100 times at every size instead of using one sample.

`timings.csv` persists every raw timing row. `summary.json` contains medians and p95s.

P95 estimator: nearest-rank empirical percentile, `sorted(x)[ceil(0.95*n)-1]`.

Commitment-build timing here is `CoverageObligation.from_source_ids(...)`, matching the conceptual commitment primitive used by the original benchmark; it does not include source-node insertion or LLM work.

Environment is recorded in `../HARDWARE.md`.
