from pathlib import Path
import subprocess

from src.git_integration import audit_delivery, changed_files


def sh(repo: Path, *args: str) -> str:
    return subprocess.check_output(list(args), cwd=repo, text=True).strip()


def test_real_git_commit_manifest_detects_suppressed_changed_file(tmp_path: Path):
    repo=tmp_path/'repo'; repo.mkdir()
    sh(repo,'git','init','-q')
    sh(repo,'git','config','user.email','test@example.com')
    sh(repo,'git','config','user.name','Test')
    (repo/'auth.py').write_text('def ok(x): return bool(x)\n')
    (repo/'util.py').write_text('def add(a,b): return a+b\n')
    sh(repo,'git','add','.')
    sh(repo,'git','commit','-qm','base')
    base=sh(repo,'git','rev-parse','HEAD')

    (repo/'auth.py').write_text('def ok(x): return True  # security-relevant change\n')
    (repo/'util.py').write_text('def add(a,b): return a+b  # comment\n')
    (repo/'docs.txt').write_text('new docs\n')
    sh(repo,'git','add','.')
    sh(repo,'git','commit','-qm','change')
    head=sh(repo,'git','rev-parse','HEAD')

    expected=changed_files(repo,base,head)
    assert set(expected)=={'auth.py','util.py','docs.txt'}

    complete=audit_delivery(repo,base,head,expected)
    assert complete.allow
    attacked=audit_delivery(repo,base,head,tuple(x for x in expected if x!='auth.py'))
    assert not attacked.allow
    assert attacked.missing_files==('auth.py',)
