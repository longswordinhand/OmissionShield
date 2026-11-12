from pathlib import Path
import tempfile

from src.phase0 import make_cases, evaluate_omission, minimal_decisive_omission, run


def test_complete_context_passes_gate():
    for case in make_cases(n_per_domain=2):
        r = evaluate_omission(case, [])
        assert r.coverage_ok
        assert not r.whynot_detected
        assert not r.decision_flipped


def test_any_required_omission_is_detected():
    for case in make_cases(n_per_domain=2):
        r = evaluate_omission(case, [case.required_ids[0]])
        assert not r.coverage_ok
        assert r.whynot_detected


def test_micro_cases_have_decisive_single_item_omissions():
    for case in make_cases(n_per_domain=3):
        k, ids = minimal_decisive_omission(case)
        assert k == 1
        assert len(ids) == 1


def test_run_writes_results():
    with tempfile.TemporaryDirectory() as d:
        summary = run(Path(d))
        assert summary["n_cases"] == 24
        assert summary["fraction_mdo_1"] == 1.0
        assert summary["whynot_detection_on_any_omission"] == 1.0
        assert summary["false_positive_on_complete_runs"] == 0.0
