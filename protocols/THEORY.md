# OmissionShield Theory Notes

## Definitions

Let a task `q` operate over a bounded evidence source whose task-relevant source universe is `U_q`. An **evidence obligation** `Omega(q) subseteq U_q` specifies the source items whose structural presence must be accounted for before a sensitive decision may commit.

A source emits an authenticated commitment `R_q = Commit(Omega(q))`. The agent pipeline constructs a coverage-carrying evidence DAG. Source nodes correspond to immutable source evidence IDs; derived nodes explicitly name parent evidence IDs. For terminal decision artifacts `T`, let `Closure_src(T)` be the set of source evidence IDs reachable from `T` through parent edges.

A **Selective Evidence Suppression (SES)** adversary removes one or more required source items or their structural dependencies from the source-to-decision path while preserving the truth and validity of all evidence that remains visible.

Evidence Completeness Integrity (ECI) for a strict obligation requires:

`Omega(q) subseteq Closure_src(T)`

except for evidence covered by an explicit policy-approved drop certificate.

## Proposition 1 — Observation-equivalence impossibility

Consider any verifier `V` whose input consists only of the delivered evidence set `E` and metadata computed solely from members of `E` (e.g., signatures, integrity labels, positive provenance, or content features). Without an independent signal describing the expected bounded evidence universe, `V` cannot distinguish a world in which `E` is complete from a world in which a required item was silently suppressed before observation.

### Proof

Construct two worlds.

- `W0`: the complete required evidence universe is exactly `E`.
- `W1`: the complete required evidence universe is `E union {x}`, where `x` is required but is removed before the verifier observes the pipeline.

By construction, the delivered evidence and all metadata derived solely from delivered items are identical in `W0` and `W1`. Therefore a deterministic verifier receives identical inputs and must return the same output in both worlds. A randomized verifier receives the same input distribution and therefore has the same output distribution. Consequently, a verifier that accepts the complete benign world `W0` cannot reliably reject the omission world `W1` without an independent expected-set signal. QED.

### Interpretation

The proposition does not claim that IFC, signatures, causal attribution, or positive provenance are ineffective at their intended goals. It identifies an information boundary: validating what is present cannot, by itself, certify that a required item is absent only because it never existed.

## Theorem 1 — No silent structural suppression under ECI

Assume:

1. The bounded source correctly enumerates the task obligation `Omega(q)` and emits an authenticated commitment `R_q`.
2. The adversary cannot forge the source commitment or evidence IDs.
3. Every derived evidence node accepted by the control plane explicitly declares its parent evidence IDs.
4. The decision gate accepts only if the observed source commitment matches `R_q` and every required ID is in `Closure_src(T)` or has a policy-approved drop certificate.

Then an adversary cannot silently suppress any required source evidence item while causing the gate to accept, unless it violates at least one assumption above.

### Proof

Let `x in Omega(q)` be a required item suppressed by the adversary. If `x` is not represented in the terminal source closure and lacks an approved drop certificate, then `x in Omega(q) \ Closure_src(T)`. The gate computes this set difference and rejects. To make the gate accept, the adversary must either (a) introduce `x` into the structural closure, (b) forge or alter the obligation/commitment so that `x` is no longer required, (c) forge an approved drop record, or (d) violate the parent-declaration semantics. Options (b)-(d) contradict the assumptions; option (a) means `x` was not structurally suppressed. Therefore silent structural suppression and gate acceptance cannot coexist under the stated assumptions. QED.

## Corollary — Positive-provenance compatibility

OmissionShield can be composed with positive provenance and IFC. ECI constrains expected source-set coverage; existing mechanisms can independently constrain confidentiality, integrity labels, source ancestry, or action authorization. ECI is orthogonal to those properties.

## Explicit non-theorem: semantic faithfulness

If a derived node declares all required parents but its natural-language payload semantically ignores or misrepresents a parent, structural ECI may still pass. OmissionShield v1 does not prove semantic preservation through arbitrary LLM transformations. This is intentionally excluded from the security guarantee.

## Open-world boundary

For open-world retrieval where no trusted component can define or commit to an expected evidence universe, Proposition 1 applies. OmissionShield may use heuristic coverage signals in such settings, but the deterministic ECI guarantee is restricted to bounded/enumerable or commitment-capable sources.
