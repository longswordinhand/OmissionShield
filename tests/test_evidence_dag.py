from src.evidence_dag import CoverageObligation, EvidenceDAG, why_not_gate


def test_derived_summary_can_carry_structural_coverage_without_hashing_text():
    dag = EvidenceDAG()
    for eid in ["e1", "e2", "e3"]:
        dag.add_source(eid, payload=eid)
    dag.add_derived("summary", ["e1", "e2", "e3"], payload="free-form semantic summary")
    obl = CoverageObligation.from_source_ids("task", ["e1", "e2", "e3"])
    dec = why_not_gate(dag, obl, ["summary"], obl.source_root)
    assert dec.allow


def test_silent_parent_omission_is_detected():
    dag = EvidenceDAG()
    for eid in ["e1", "e2", "e3"]:
        dag.add_source(eid, payload=eid)
    dag.add_derived("summary", ["e1", "e3"], payload="summary omitted e2 structurally")
    obl = CoverageObligation.from_source_ids("task", ["e1", "e2", "e3"])
    dec = why_not_gate(dag, obl, ["summary"], obl.source_root)
    assert not dec.allow
    assert dec.missing_ids == frozenset({"e2"})


def test_explicit_policy_approved_drop_is_not_silent():
    dag = EvidenceDAG()
    for eid in ["e1", "e2", "e3"]:
        dag.add_source(eid, payload=eid)
    dag.record_drop("e2", "policy-approved privacy minimization", policy_approved=True)
    dag.add_derived("summary", ["e1", "e3"], payload="summary")
    obl = CoverageObligation.from_source_ids("task", ["e1", "e2", "e3"])
    dec = why_not_gate(dag, obl, ["summary"], obl.source_root)
    assert dec.allow


def test_declared_parent_does_not_claim_semantic_faithfulness():
    dag = EvidenceDAG()
    for eid in ["e1", "e2"]:
        dag.add_source(eid, payload=eid)
    # Structural coverage passes even if the natural-language summary is poor.
    dag.add_derived("summary", ["e1", "e2"], payload="mentions only e1 semantically")
    obl = CoverageObligation.from_source_ids("task", ["e1", "e2"])
    assert why_not_gate(dag, obl, ["summary"], obl.source_root).allow
