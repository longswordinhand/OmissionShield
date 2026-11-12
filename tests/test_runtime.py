from src.runtime import TrustedEvidenceRuntime


def test_runtime_owned_edges_detect_real_suppression():
    rt=TrustedEvidenceRuntime(b'k')
    signed=rt.enumerate_source('t',[('a','A'),('b','B'),('c','C')])
    rt.deliver('s1',['a','c'])
    rt.commit_derived('s1','summary','free text')
    dec=rt.gate(signed,['summary'])
    assert not dec.allow and dec.missing_ids==frozenset({'b'})


def test_model_cannot_self_report_parent_edge():
    rt=TrustedEvidenceRuntime(b'k')
    signed=rt.enumerate_source('t',[('a','A'),('b','B')])
    rt.deliver('s1',['a'])
    # Payload can lie and claim b, but the runtime parent is still only a.
    rt.commit_derived('s1','summary','I used a and b')
    dec=rt.gate(signed,['summary'])
    assert not dec.allow and 'b' in dec.missing_ids


def test_signed_obligation_rejects_forgery():
    rt=TrustedEvidenceRuntime(b'k')
    signed=rt.enumerate_source('t',[('a','A')])
    forged=type(signed)(signed.task_id,('a','b'),signed.source_root,signed.signature)
    assert not rt.verify_obligation(forged)
