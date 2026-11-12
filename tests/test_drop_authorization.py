from dataclasses import replace

import pytest

from src.runtime import TrustedEvidenceRuntime


KEY = b"drop-auth-test-key"


def _runtime_with_obligation():
    rt = TrustedEvidenceRuntime(KEY)
    signed = rt.enumerate_source("task-1", [("e1", "A"), ("e2", "B")])
    return rt, signed


def test_valid_authenticated_drop_allows_named_missing_evidence():
    rt, signed = _runtime_with_obligation()
    auth = rt.issue_drop_authorization(
        signed, "e2", principal="privacy-policy", reason="minimize sensitive field", nonce="n1"
    )
    rt.apply_drop_authorization(signed, auth)
    rt.deliver("stage", ["e1"])
    rt.commit_derived("stage", "summary", "summary of e1")
    dec = rt.gate(signed, ["summary"])
    assert dec.allow
    assert dec.approved_drop_ids == frozenset({"e2"})


def test_forged_drop_signature_is_rejected():
    rt, signed = _runtime_with_obligation()
    auth = rt.issue_drop_authorization(signed, "e2", "policy", "reason", "n2")
    forged = replace(auth, signature="0" * len(auth.signature))
    with pytest.raises(ValueError, match="invalid drop authorization"):
        rt.apply_drop_authorization(signed, forged)


def test_drop_authorization_is_task_bound():
    rt = TrustedEvidenceRuntime(KEY)
    signed1 = rt.enumerate_source("task-1", [("e1", "A"), ("e2", "B")])
    signed2 = rt.enumerate_source("task-2", [("x1", "X"), ("x2", "Y")])
    auth = rt.issue_drop_authorization(signed1, "e2", "policy", "reason", "n3")
    with pytest.raises(ValueError, match="invalid drop authorization"):
        rt.apply_drop_authorization(signed2, auth)


def test_drop_authorization_is_source_version_bound():
    rt_old, signed_old = _runtime_with_obligation()
    auth = rt_old.issue_drop_authorization(signed_old, "e2", "policy", "reason", "n4")

    rt_new = TrustedEvidenceRuntime(KEY)
    signed_new = rt_new.enumerate_source("task-1", [("e1", "A"), ("e2", "B"), ("e3", "C")])
    with pytest.raises(ValueError, match="invalid drop authorization"):
        rt_new.apply_drop_authorization(signed_new, auth)


def test_drop_authorization_nonce_cannot_be_replayed():
    rt, signed = _runtime_with_obligation()
    auth = rt.issue_drop_authorization(signed, "e2", "policy", "reason", "n5")
    rt.apply_drop_authorization(signed, auth)
    with pytest.raises(ValueError, match="replayed drop authorization"):
        rt.apply_drop_authorization(signed, auth)
