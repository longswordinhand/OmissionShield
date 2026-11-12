from src.phase1_multimodel import make_cases


def test_phase1_case_count_and_position_balance():
    cases = make_cases()
    assert len(cases) == 60
    assert sum(c.domain == 'code_review' for c in cases) == 30
    assert sum(c.domain == 'soc' for c in cases) == 30
    for pos in ['first','middle','last']:
        assert sum(c.decisive_position == pos for c in cases) == 20
