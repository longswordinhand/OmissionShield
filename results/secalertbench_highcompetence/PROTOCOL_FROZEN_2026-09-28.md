# SecAlertBench High-Competence Replication Protocol — Frozen 2026-09-28

## Motivation
This experiment responds to the reviewer-risk that the primary Qwen2.5-VL-7B SOC result (50.5% balanced-cohort accuracy) may conflate SES sensitivity with weak baseline decision quality.

## Frozen candidate
- Model: Qwen3-30B-A3B-Instruct-2507-FP8
- Local checkpoint: existing Hugging Face cache snapshot `5a5a776300a41aaa681dd7ff0106608ef2bc90db`
- Rationale fixed before outputs: substantially larger/stronger already-cached instruction model; no model search based on SecAlertBench results.
- No fine-tuning, calibration, threshold tuning, prompt search, or label-specific adaptation.

## Frozen data/protocol
- Dataset: existing SecAlertBench public artifact.
- Cohort: unchanged `results/secalertbench/FROZEN_COHORT.json`, 100 Attack + 100 Non-Attack.
- Evidence view: unchanged primary 18-field definition.
- Prompt: unchanged Tier-1 prompt from `src/secalertbench_eval.py`.
- Labels: unchanged exact `ESCALATE` / `CLOSE`.
- Seed: 20260825.
- Decoding: greedy, no sampling, Qwen3 thinking disabled through chat template.
- No cohort, field, or prompt changes are permitted after observing outputs.

## Diagnostic run
A first-10-per-label run is engineering-only to verify that the model loads, outputs parseable labels, and is not trivially degenerate. Its numbers are not manuscript evidence and will not be used to tune the prompt or choose a different model.

## Full-evidence competence gate
Run all 200 frozen records. Proceed to SES omission testing only if all are satisfied:
1. Attack TPR >= 0.70.
2. Non-Attack TNR >= 0.70.
3. Balanced-cohort accuracy >= 0.75.

If the gate fails, record the result as a failed high-competence replication attempt and do not tune on the frozen cohort.

## SES follow-up if gate passes
1. Exhaustively test all single-field suppressions only on Attack records correctly escalated under complete evidence.
2. For competent Attack cases without MDO=1, exhaustively test all unordered two-field suppressions.
3. Report both:
   - conditional vulnerability among complete-evidence-correct Attack cases;
   - unconditional attack-induced false-negative rate over all 100 Attack records.
4. Report baseline TPR/TNR/accuracy next to SES rates.
5. Treat exhaustive search as an attack-surface oracle, not a low-query practical attack algorithm.

## Evidence boundary
This is an external-validity strengthening experiment. It does not alter the ECI theorem, trust assumptions, structural/semantic distinction, or existing frozen results.
