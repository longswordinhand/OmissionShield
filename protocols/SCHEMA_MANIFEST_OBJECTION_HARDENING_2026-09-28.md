# Schema / Manifest / Provenance Objection Hardening — 2026-09-28

## Reviewer objection
“Why is this not just schema validation, manifest checking, or another provenance gate?”

## Resolution
Added Table 6 comparing five mechanism classes by the reference information available at decision commit and the kind of absence they can establish:

1. Fixed-schema validation
2. Direct manifest comparison
3. Positive provenance / evidence tracing
4. Runtime provenance / task-effect gates (AGATE, TraceGrant)
5. OmissionShield / ECI

## Key distinction
### Fixed schema
Sufficient when the object to be protected is itself a fixed required field visible to the final verifier.

### Direct manifest comparison
Sufficient when:
- the final trusted verifier has the expected object-ID set; and
- every original source ID is forwarded unchanged to that verifier.

In that special case, OmissionShield's evidence DAG is unnecessary.

### Positive provenance
Can establish origin and ancestry for evidence that was admitted to the trace, but cannot by itself determine that an expected source member never entered the trace.

### Runtime provenance / task-effect gates
Overlap substantially with OmissionShield in deterministic runtime enforcement and provenance. The paper does not claim those mechanisms in isolation as novel. Their published descriptions are not treated as establishing expected source-membership completeness for pre-trace omitted members.

### OmissionShield / ECI
Adds:
- authenticated task-specific expected source membership;
- missing-member security property;
- transitive source closure through transformed evidence;
- fail-closed decision-commit check.

## Why the DAG is needed
The DAG is not needed merely to compare two sets.
It is needed when:
- the expected source set is task-dependent;
- evidence is summarized, aggregated, minimized, or distributed;
- raw source IDs/payloads are not all forwarded unchanged to the final component;
- the final commit still requires accountability to original source obligations.

This is the precise regime in which terminal schema validation or direct manifest equality is insufficient.

## Visual QA
- Table appears on page 11.
- No clipping or overflow.
- All columns readable.
- LaTeX build passes.
- No undefined citations/references.
- No overfull boxes.
- Manuscript remains 12 pages.

## Claim boundary
Allowed:
“OmissionShield generalizes beyond the simple manifest-comparison special case by preserving task-specific source coverage through transformed evidence.”

Not allowed:
“Schema validation or manifest checking can never solve completeness.”

