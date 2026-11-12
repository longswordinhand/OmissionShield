# L230 exhaustiveness correction

## What the code actually does

`src/tqrg_llm_eval.py::eval_commit` loops over:

`for k in range(1, min(max_k, len(files)-1)+1)`

with `max_k=2` by default. Therefore it never evaluates a removal that leaves zero files. For a 2-textual-file commit, only the two single-file removals are tested; the remove-both subset is excluded.

The search also stops after the first omission budget `k` that produces at least one target flip, so the appropriate expected subset total for a competent case is: all singles, plus all pairs only if no single-file flip occurred and a pair would leave at least one file.

## Independent recount from frozen Qwen3 trials

Cohort A (`results/tqrg_real/llm_qwen3/trials.jsonl`):
- Competent cases: 16
- Expected tested subsets under “singles, then all pairs if needed, including the degenerate empty pair”: 77
- Actual recorded subsets: 75
- Difference: 2, exactly the two omitted empty-evidence pair queries below.

Cohort B (`results/tqrg_holdout/llm_qwen3/trials.jsonl`):
- Competent cases: 24
- Expected under the same counterfactual exhaustive wording: 100
- Actual recorded subsets: 95
- Difference: 5, exactly the five omitted empty-evidence pair queries below.

The seven competent, two-textual-file, non-flipping commits for which the remove-both subset was never tested are:

Cohort A:
- CVE-2011-4969
- CVE-2017-14695

Cohort B:
- CVE-2018-18837
- CVE-2017-16910
- CVE-2019-13574
- CVE-2014-4987
- CVE-2016-9468

This independently agrees with Muse's list and the 77-vs-75 / 100-vs-95 totals.

## Corrected L230 sentence

Recommended replacement:

> For every competent case, we exhaustively removed all one-file subsets and, when no one-file attack succeeded, all two-file subsets that left at least one textual file in the prompt.

This is accurate against the executed Qwen3 code and frozen trial files.

## Empty-subset protocol asymmetry disclosure

> The Qwen3 search excluded the degenerate subset that removes all textual files, whereas the Qwen2.5-VL pair-search code evaluated all two-file combinations, including remove-all cases for two-file commits; those 7B empty-input queries did not change the reported attack-induced-miss counts.

## Optional empty-evidence rerun decision

**Not run.** The current local Ollama manifest verifies that today's `qwen3:latest` is an 8.2B Q4_K_M artifact with model-layer digest `sha256:a3de86cd...`, but the historical Qwen3 trial artifacts recorded only the mutable tag `qwen3:latest`, not its digest. Therefore we cannot establish that the current digest is identical to the model used for the frozen runs. Under the Phase-1 rule, no new 21-query empty-evidence run was performed.

## Count impact

No existing scientific count was changed. The frozen Qwen3 result remains 26 additional attack-induced misses across the 49-commit cohort; this file corrects the protocol description only.
