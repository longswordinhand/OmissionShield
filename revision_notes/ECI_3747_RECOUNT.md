# Independent recount of the 3,747 ECI headline

## Inputs

- `results/secalertbench/FROZEN_COHORT.json`
- `data/public/secalertbench/secalertbench.json`
- `results/secalertbench/eci/trials.jsonl`
- `results/tqrg_real/eci/trials.jsonl`
- `results/tqrg_holdout/eci/trials.jsonl`

No frozen artifact was modified.

## Recompute method

1. Read the 18 schema fields from `FROZEN_COHORT.json::fields_primary`.
2. Resolve each of the 200 frozen records by its stored dataset `index` into `secalertbench.json`.
3. Treat a field as present iff its value is neither `null` nor the empty string.
4. Count nonempty schema fields per frozen alert.
5. For each frozen alert, count each of the 18 schema fields as present or absent and sum over 200 alerts.
6. Independently confirm that `results/secalertbench/eci/trials.jsonl` contains exactly 3,600 rows (=200 x 18), one omitted schema-field handle per row.
7. Count Git ECI `variant=suppress1` rows in the two frozen Git cohorts.

## SOC nonempty-field counts

Histogram of nonempty fields per alert:

| Nonempty fields | Alerts |
|---:|---:|
| 12 | 2 |
| 13 | 5 |
| 14 | 17 |
| 15 | 56 |
| 16 | 42 |
| 17 | 62 |
| 18 | 16 |

- Range: **12–18**
- Median: **16**
- Alerts with all 18 fields present: **16/200**

Therefore the manuscript sentence implying that every alert exposes 18 actual evidence fields is false. Eighteen is the **schema size**, not the per-alert nonempty evidence count.

## 3,600 SOC schema-item checks: present vs absent

Across 200 alerts x 18 schema fields:

- Present-field removals: **3,181**
- Already-absent field placeholders: **419**
- Total schema-item checks: **3,600**

Absent-field breakdown:

| Field | Already absent in frozen alerts |
|---|---:|
| `xff` | 173 |
| `req_body` | 107 |
| `parameter` | 63 |
| `rsp_body` | 51 |
| `rsp_header` | 19 |
| `host` | 6 |
| **Total** | **419** |

All other schema fields were nonempty in all 200 frozen records.

## Git structural-removal count

- Cohort A: `57` rows with `variant=suppress1`
- Cohort B: `90` rows with `variant=suppress1`
- Git genuine single-file removals: **147**

Thus:

**147 Git + 3,181 SOC present-field removals = 3,328 genuine evidence removals.**

The larger **3,747** number is valid only as **147 Git evidence removals + 3,600 SOC schema-item suppression checks**. Of those SOC checks, 419 remove handles representing fields whose payload was already absent/null in that alert.

## Corrected wording for the manuscript Abstract

Recommended precise wording:

> Across Git and SOC structural traces, ECI rejected all 3,328 tested single-item removals of actually present evidence with exact missing-ID attribution while admitting every complete trace. The SOC evaluation additionally included 419 schema-item checks in which the omitted handle represented a field already absent in the released alert record; these are reported separately rather than counted as evidence removals.

If the authors prefer to preserve the 3,747 total, use instead:

> Across Git and SOC structural traces, ECI rejected all 3,747 tested schema-item suppressions with exact missing-ID attribution, including 3,328 removals of actually present evidence and 419 SOC checks that removed already-absent field placeholders, while admitting every complete trace.

## Agreement with Muse audit

This independent recount **agrees exactly** with Muse: 3,328 genuine removals and 419 absent-field placeholders, with absent-field breakdown `xff=173`, `req_body=107`, `parameter=63`, `rsp_body=51`, `rsp_header=19`, `host=6`.
