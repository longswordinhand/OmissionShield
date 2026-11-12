# Frozen Pair-Omission Follow-up Protocol

Frozen on 2026-08-25 after the pre-registered single-field primary analysis was completed for Qwen2.5-VL-7B, and before any two-field omission outputs were generated.

## Rule
For each model and each frozen SecAlertBench Attack record:
1. include the record only if the model returns ESCALATE under the complete primary evidence view;
2. if any single nonempty field omission changes ESCALATE to CLOSE, assign MDO=1 and do not evaluate pairs;
3. otherwise exhaustively evaluate all unordered pairs of nonempty primary evidence fields;
4. assign MDO=2 if at least one pair changes ESCALATE to CLOSE;
5. otherwise record no flip within budget two.

The frozen record cohort, primary evidence fields, and model prompts are unchanged. No record, alert type, or field may be added or removed based on pair-omission outcomes.

The content-only sensitivity analysis is separate and is not used to redefine the primary evidence universe.
