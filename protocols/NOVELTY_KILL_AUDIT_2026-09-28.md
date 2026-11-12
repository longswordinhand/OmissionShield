# OmissionShield Novelty Kill Audit — 2026-09-28

## One-sentence paper identity
For security-sensitive LLM-agent decisions over bounded evidence sources, OmissionShield identifies selective removal of truthful required evidence as a distinct attack surface, proves that delivered evidence alone cannot certify expected-set completeness, and enforces an authenticated expected-set obligation through a coverage-carrying evidence DAG at decision commit.

Dominant identity:
1. theory/limit result: observation-equivalence boundary for positive-only completeness verification;
2. security-property contribution: Evidence Completeness Integrity (ECI);
3. systems mechanism: authenticated expected-set commitment + transitive coverage/negative provenance + fail-closed commit gate;
4. empirical attack-surface measurement: small targeted omissions can reverse otherwise-correct security judgments.

## Fatal-flaw gate

### Likely duplication
**Finding: no direct duplicate retrieved under the current searches.**
This is not a proof of novelty.

Closest systems:
- AGATE (arXiv:2609.30830, 2026-09-25): deterministic authorization + data-provenance gate at agent-harness boundaries; source registration connects observed inputs to transfers; effect ledger governs repeated requests.
- Correct Is Not Governed / Matrix (arXiv:2608.12761): deterministic causal-state layer and authored completeness contracts; importantly reports transfer failure of a completeness contract.
- TraceGrant (arXiv:2608.21126): trusted task-effect contract, runtime evidence, tool effects, completion verification.
- Authenticated Workflows (arXiv:2602.10465): cryptographic trust layer over prompt/tool/data/context boundaries.
- Fides (arXiv:2505.23643): information-flow labels and deterministic policy enforcement.
- evidence/provenance survey (arXiv:2606.04990): traces evidence dependencies and execution provenance.
- Rajan et al. (arXiv:2607.22448): taxonomy and attribution of information omission through agent pipelines.

None of the retrieved descriptions states the exact OmissionShield combination:
(a) independently enumerated expected source-membership set;
(b) impossibility of proving that set complete from delivered members alone;
(c) runtime propagation of transitive source coverage through transformed evidence;
(d) commit-time rejection based on missing expected members rather than only invalid/unauthorized observed members.

### Core mechanism refuted by user data
No.
- ECI structurally rejected all tested single-item suppressions in the implemented bounded-source settings.
- multi-stage tests preserved source-deficit attribution through aggregation.
- cross-process gateway blocked the protected effect before the tool boundary.

### No discriminating experiment
No fatal issue.
The high-competence Git result distinguishes SES from “the model was already bad”:
- Qwen2.5-VL-7B: 44/49 complete-evidence correct (89.8%).
- targeted suppression caused 20/49 additional correct-to-wrong reversals (40.8% unconditional).

The SOC domain is not suitable as a co-equal headline robustness result and has been demoted to secondary stress-test status.

### Evaluation leakage / invalid target
No critical flaw identified.
- frozen cohorts and intervention protocols exist;
- exhaustive MDO is now explicitly framed as an attack-surface oracle/existence test, not a practical attacker with free search;
- conditional and unconditional attack-impact rates are separated.

### Contribution collapses to packaging
No, provided the paper does **not** claim the runtime gate/provenance graph alone as the novelty.
The paper collapses toward packaging if framed as “another provenance gate.”
It remains scientifically distinct if framed around:
1. expected-set completeness as the protected object;
2. observation-equivalence as the necessity result;
3. negative provenance/transitive source coverage as the enforcement primitive.

## Closest-neighbor axis comparison

| Work | Main protected object | Starts from observed/admitted evidence | Independent expected source-membership set | Explicit absent-member security property | Commit-time deterministic enforcement |
|---|---|---:|---:|---:|---:|
| Fides | IFC labels / data-flow policy | yes | not retrieved | no | yes |
| Authenticated Workflows | authenticity + policy across workflow boundaries | yes / authenticated objects | not retrieved | no | yes |
| TraceGrant | trusted task intent to realized effect/completion | yes | not retrieved | no | yes |
| Matrix | governed authority/fact/task completion contracts | contract-defined obligations | partial conceptual overlap | completeness contract, but not retrieved as source-member absence | yes |
| AGATE | authorization + provenance of data carried into effects | source registration of observed inputs | not retrieved | no source-member absence claim retrieved | yes |
| OmissionShield | completeness of task-required bounded source membership | **no: compares against external expected set** | **yes** | **yes: ECI** | **yes** |

The table should be read conservatively: “not retrieved” means the current literature search did not find that feature in the published description; it does not prove absence from every implementation detail.

## Reviewer kill routes

### Kill route A: “This is just provenance + schema validation.”
Severity: MAJOR.
Defense:
- Proposition 1: positive provenance cannot establish expected-set completeness without an independent expected-set signal.
- task-dependent expected sets + transformed/aggregated evidence distinguish OmissionShield from fixed terminal schemas.
- transitive source closure preserves accountability when raw payloads are summarized or distributed.

Action:
Make this distinction visible in the first two pages and Figure 1, not only in Discussion.

### Kill route B: “AGATE/TraceGrant/Matrix already provide deterministic provenance gates.”
Severity: MAJOR after 2026-09-25 AGATE release.
Defense:
Concede overlap at enforcement/provenance layer. Claim novelty only for the protected object and associated theorem:
expected-set membership completeness and negative provenance for silent source suppression.

Action:
Cite AGATE and Matrix explicitly and state that runtime enforcement is not novel in isolation. Completed in current manuscript.

### Kill route C: “The trusted source enumerator assumes the hard part.”
Severity: MAJOR but bounded.
Defense:
Observation equivalence establishes that some independent expected-set authority is necessary. The contribution is trust localization and enforcement downstream, not source-authority elimination.

### Kill route D: “Semantic suppression is more realistic.”
Severity: MAJOR scope objection, not theorem invalidity.
Defense:
Keep structural completeness and semantic faithfulness disjoint. Do not imply ECI solves semantic misrepresentation.

### Kill route E: “Headline empirical result depends on weak SOC models.”
Severity: previously MAJOR, now substantially reduced.
Defense:
Git is primary empirical domain; SOC is secondary stress test. High-competence 30B calibrated SOC replication failed the predeclared competence gate and was stopped before SES testing.

## Contribution-result contract

### C1 — Observation-equivalence boundary
Status: VALIDATED as a formal argument in the manuscript.
Claim allowed:
A verifier whose view is restricted to delivered evidence and metadata derived only from it cannot distinguish a complete set from a larger expected set whose missing member was removed before observation.

### C2 — ECI as a security property
Status: VALIDATED within bounded/commitment-capable sources and stated TCB.
Claim allowed:
ECI can deterministically prevent silent structural suppression after a correct expected-set commitment.

### C3 — Coverage-carrying evidence DAG / WhyNotGate
Status: VALIDATED as an implementation of C2, not novel merely because it is a runtime gate.
Claim allowed:
It carries transitive source coverage through multi-stage transformations and blocks protected commit when obligated source coverage disappears.

### C4 — SES has measurable decision consequence
Status: VALIDATED in the Git/CVE setting; secondary evidence in SOC.
Strongest empirical statement:
A 7B model with 89.8% complete-evidence accuracy suffered 40.8% additional correct-to-wrong reversals over the full 49-commit cohort under the tested <=2-deletion oracle.

### C5 — production prevalence / semantic attack robustness
Status: NOT VALIDATED and should not be claimed.

## Strategic judgment
**DECISION: PROCEED AFTER REVISION.**

There is no established fatal novelty collapse.

The paper is publishable only if its identity is kept narrow:
**not “a new provenance runtime,” but “expected-set completeness as a security property, its positive-only impossibility boundary, and a negative-provenance enforcement mechanism for selective evidence suppression.”**

The new AGATE paper increases the cost of vague systems novelty claims, but it does not, based on the retrieved published description, subsume the expected-set completeness problem or the observation-equivalence result.

## Top next actions
1. Rebuild Figure 1 / first-page framing so positive provenance versus negative expected-set completeness is visually undeniable.
2. Add a compact nearest-neighbor comparison in the manuscript if page budget permits, including AGATE and Matrix.
3. Perform one final reviewer pass asking only: “Could a skeptical reader still summarize this as schema validation plus a provenance gate?” If yes, revise until the answer is clearly no.

## Frozen contribution
Selective Evidence Suppression + Evidence Completeness Integrity + observation-equivalence boundary + authenticated expected-set/coverage enforcement.

## Claims allowed
- structural source-membership completeness under stated bounded-source/TCB assumptions;
- deterministic rejection of tested structural omissions;
- targeted omission fragility in the Git/CVE benchmark;
- SOC only as secondary structural stress-test evidence.

## Claims not allowed
- semantic-faithfulness security;
- source-enumerator compromise resistance;
- open-world completeness;
- production prevalence;
- novelty of provenance graphs, runtime gates, or deterministic policy enforcement by themselves.
