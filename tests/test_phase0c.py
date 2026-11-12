from src.phase0c_llm import make_cases, normalize


def test_case_balance():
    cases = make_cases()
    assert len(cases) == 20
    assert sum(c.domain == "code_review" for c in cases) == 10
    assert sum(c.domain == "soc" for c in cases) == 10


def test_normalize():
    assert normalize("code_review", "SECURITY_ISSUE") == "SECURITY_ISSUE"
    assert normalize("soc", "CLOSE") == "CLOSE"
