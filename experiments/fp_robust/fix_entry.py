"""Version 2 entrypoint repair; preserve v1 bytes and invalid smoke rows."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
base = (ROOT / 'releases/exp039-c26/main.py').read_bytes()
for tag in 'ab':
    target = OUT / f'variant_{tag}_v2.py'
    assert not target.exists()
    target.write_bytes(base + b'\n\n' + (OUT / f'append_{tag}.py').read_bytes())
    print(target.name, hashlib.sha256(target.read_bytes()).hexdigest())
for name in ('smoke', 'dev', 'holdout', 'fresh', 'closed'):
    source = OUT / f'jobs_{name}.json'
    target = OUT / f'jobs_{name}_v2.json'
    assert not target.exists()
    jobs = json.loads(source.read_text())
    for job in jobs:
        if job[0] in ('a', 'b'):
            job[1] = f'experiments/fp_robust/variant_{job[0]}_v2.py'
    target.write_text(json.dumps(jobs, separators=(',', ':')) + '\n')
    print(target.name, hashlib.sha256(target.read_bytes()).hexdigest())
