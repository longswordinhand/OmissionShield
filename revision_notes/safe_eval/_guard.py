from pathlib import Path

PROJECT_ROOT = Path('/home/yguo56/projects/OmissionShield').resolve()
FROZEN_RESULTS = (PROJECT_ROOT / 'results').resolve()

def guarded_out(path: str, force: bool) -> Path:
    p = Path(path).resolve()
    if not force and (p == FROZEN_RESULTS or FROZEN_RESULTS in p.parents):
        raise SystemExit(f'Refusing to write under frozen results/: {p}. Choose revision_2026-11-10/ or /tmp, or pass --force explicitly.')
    return p
