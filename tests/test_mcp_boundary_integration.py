from src.mcp_boundary_integration import run_once


def test_complete_tool_boundary_commits_under_protection():
    out = run_once(suppress=False, protected=True)
    assert out["commit_allowed"] is True
    assert out["gate_reason"] == "COVERAGE_SATISFIED"


def test_suppressed_tool_result_is_blocked_before_sensitive_tool_call():
    unprotected = run_once(suppress=True, protected=False)
    protected = run_once(suppress=True, protected=True)
    assert unprotected["commit_allowed"] is True
    assert protected["commit_allowed"] is False
    assert protected["missing"] == ["auth.py"]
    assert protected["gate_reason"] == "SILENT_REQUIRED_EVIDENCE_OMISSION"
