from src.coverage import (
    certify_delivery,
    ifc_label_gate,
    make_obligation,
    positive_provenance_gate,
    why_not_gate,
)


def test_observation_equivalence_positive_provenance_cannot_see_absence():
    observed = ["f1", "f2", "f3", "f4"]
    # W0: observed is complete. W1: f5 existed but was omitted. A positive-only
    # verifier receives the same observed set and valid ancestry in both worlds.
    assert positive_provenance_gate(observed, observed)
    assert positive_provenance_gate(observed, ["f1", "f2", "f3", "f4", "f5"])
    assert ifc_label_gate(observed, observed)


def test_negative_provenance_distinguishes_bounded_omission_world():
    expected = ["f1", "f2", "f3", "f4", "f5"]
    obligation = make_obligation("commit-X", expected)
    cert = certify_delivery(["f1", "f2", "f3", "f4"], obligation.source_manifest_root)
    ok, missing = why_not_gate(obligation, cert)
    assert not ok
    assert missing == frozenset({"f5"})


def test_complete_delivery_passes():
    expected = ["a", "b", "c"]
    obligation = make_obligation("task", expected)
    cert = certify_delivery(expected, obligation.source_manifest_root)
    ok, missing = why_not_gate(obligation, cert)
    assert ok
    assert not missing
