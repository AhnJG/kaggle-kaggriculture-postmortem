"""Build the two preregistered standalone variants inside fp_robust only."""
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
base = (ROOT / 'releases/exp039-c26/main.py').read_bytes()
for tag in 'ab':
    append = (OUT / f'append_{tag}.py').read_bytes()
    target = OUT / f'variant_{tag}.py'
    if target.exists():
        raise SystemExit(f'refuse overwrite: {target}')
    target.write_bytes(base + b'\n\n' + append)
    print(tag, hashlib.sha256(target.read_bytes()).hexdigest(), target)
