from src.controlled_bench import make_cases, mdo, decide


def test_controlled_cases_and_mdo():
    cases=make_cases()
    assert len(cases)==60
    for c in cases:
        assert decide(c,c.items)==c.baseline_decision
        k,omit=mdo(c)
        assert k in {1,2,3}
        kept=[x for j,x in enumerate(c.items) if j not in omit]
        assert decide(c,kept)==c.target_decision
