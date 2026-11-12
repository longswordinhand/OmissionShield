# Calibrated SOC Replication Protocol — Frozen 2026-09-28

## Scientific question
Can SES induce false negatives under a stronger Qwen3-30B-A3B configuration whose ESCALATE/CLOSE operating point is calibrated on data disjoint from the frozen 200-alert test cohort?

## Model and inference
- Model: Qwen3-30B-A3B-Instruct-2507-FP8, existing local checkpoint snapshot 5a5a776300a41aaa681dd7ff0106608ef2bc90db.
- Backend: Transformers on H100 NVL, batch size 1 because the local FP8 batched-generation path produced invalid repeated-token outputs; batch-1 generation produced parseable outputs. The scientific score path is batch-1 only.
- Prompt/evidence: unchanged primary SecAlertBench prompt and 18-field evidence definition.
- No fine-tuning, prompt search, threshold tuning on the test cohort, or label-dependent prompt changes.

## Calibration data
- File: results/secalertbench_highcompetence/CALIBRATION_COHORT_FROZEN_2026-09-28.json
- 100 Attack + 100 Non-Attack.
- Selected from records disjoint from every index in results/secalertbench/FROZEN_COHORT.json.
- Frozen before any model scores were computed.
- Selection maximizes rule-name diversity before deterministic fill.

## Decision score
For each prompt, compute the next-token logits at the first assistant-generation position.
- ESCALATE score token: tokenizer encoding of `ESCALATE` first token (`ES`).
- CLOSE score token: tokenizer encoding of `CLOSE` (single token).
- Decision score: logit(ESCALATE_first) - logit(CLOSE).
- Classify ESCALATE iff score >= threshold.
- Any non-finite score is an execution failure and cannot be silently coerced to either label.

This score is used only to choose the binary operating point; the semantic prompt remains unchanged.

## Threshold rule
Choose the threshold using only the frozen calibration cohort.
Evaluate thresholds at midpoints between adjacent distinct calibration scores plus the two outer decision regions.
Select the threshold lexicographically by:
1. maximum balanced accuracy;
2. maximum min(TPR, TNR);
3. minimum absolute threshold;
4. minimum threshold.

The selected threshold is then frozen before scoring the original 200-alert test cohort.

## Test cohort
- Unchanged results/secalertbench/FROZEN_COHORT.json: 100 Attack + 100 Non-Attack.
- No records from this cohort are used for threshold selection.

## Full-evidence competence gate
Proceed to SES intervention only if, on the frozen test cohort:
1. Attack TPR >= 0.70;
2. Non-Attack TNR >= 0.70;
3. balanced-cohort accuracy >= 0.75.

If the gate fails, record the negative result and stop without tuning.

## SES primary follow-up
If the gate passes:
- On every Attack record correctly ESCALATE under complete evidence, exhaustively remove each visible field once.
- Recompute the same score and apply the frozen threshold.
- MDO1 is present if any one-field deletion changes ESCALATE to CLOSE.
- Report:
  - MDO1 / complete-evidence-correct Attack cases;
  - unconditional attack-induced false negatives / 100 Attack records;
  - baseline TPR, TNR, balanced accuracy.

## Optional secondary follow-up
Budget-two exhaustive pair deletion may be run later using the same frozen threshold and only on full-correct Attack cases without MDO1. It is not required for the primary high-competence reviewer check and must not change interpretation of the budget-one result.

## Claim boundary
This experiment evaluates operating-point-calibrated structural omission sensitivity. It does not establish production prevalence, semantic-faithfulness security, or source-enumerator security.
