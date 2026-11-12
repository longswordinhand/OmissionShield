# OmissionShield Phase 0 Threat Model (Frozen v0.1)

## Security question
Can an attacker change an evidence-dependent agent decision solely by silently removing required evidence, while leaving every observed item truthful, authorized, and provenance-valid?

## Scope
Phase 0 covers bounded evidence domains where the required evidence universe is enumerable or commitment-capable. The first two domains are code review and SOC incident triage.

## Adversary capabilities
The adversary may selectively suppress evidence items by dropping, truncating, or selectively forwarding them between a bounded source and the decision point. The adversary may choose omissions adaptively to maximize a target decision change.

## Adversary restrictions
The adversary may not modify evidence values, forge source identities, alter the user task, add explicit malicious instructions, invoke unauthorized tools, or forge the trusted source manifest/commitment.

## Security property: Evidence Completeness Integrity (ECI)
For task q with required evidence obligation Omega(q), a sensitive decision may proceed only if every structurally required evidence item is represented in the decision-time evidence closure or is covered by an explicit, policy-approved transformation certificate.

## Phase-0 guarantee target
No Silent Structural Omission: for a bounded source and fixed obligation, every required evidence item that is removed between source enumeration and the decision point must become observable to WhyNotGate.

## Non-goals
Phase 0 does not claim semantic faithfulness of arbitrary LLM summaries, open-world completeness, hallucination prevention, or prompt-injection detection.

## Kill criteria
Kill or pivot the project if existing provenance/IFC/capability defenses can naturally verify bounded evidence completeness with low utility loss, or if selective omission rarely changes decisions under realistic bounded tasks.

## Terminology note
`Omission attack` is already used in 2026 AI-control work for attacks that omit necessary **actions**. OmissionShield therefore calls its threat **Selective Evidence Suppression (SES)**: the adversarially missing object is evidence, not an action.
