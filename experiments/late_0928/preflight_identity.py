"""Verify every candidate returns byte-identical actions to v074 before step 576."""
import contextlib
import gzip
import hashlib
import io
import json
import pathlib

from kaggle_environments.agent import get_last_callable

ROOT = pathlib.Path(__file__).resolve().parents[2]
HERE = pathlib.Path(__file__).resolve().parent
PARENT = ROOT / "releases/round2-v074/main.py"
CANDIDATES = sorted((HERE / "candidates").glob("*.py"))
RAW = ROOT / "private_artifacts/v074_hosted_20260927/raw/114044162.json.gz"
replay = json.load(gzip.open(RAW))
cfg = replay["configuration"]


def load(path):
    with contextlib.redirect_stdout(io.StringIO()):
        return get_last_callable(path.read_text(), path=str(path))


def canonical(action):
    return json.dumps(action, sort_keys=True, separators=(",", ":"), default=str).encode()


parent = load(PARENT)
candidates = {path.stem: load(path) for path in CANDIDATES}
mismatches = {name: [] for name in candidates}
for step in range(576):
    obs = replay["steps"][step][0]["observation"]
    expected = canonical(parent(obs, cfg))
    for name, candidate in candidates.items():
        actual = canonical(candidate(obs, cfg))
        if actual != expected:
            mismatches[name].append(step)

result = {
    "episode": 114044162,
    "seat": 0,
    "steps_checked": 576,
    "parent_sha256": hashlib.sha256(PARENT.read_bytes()).hexdigest(),
    "candidates": {
        path.stem: {
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "mismatch_count": len(mismatches[path.stem]),
            "mismatch_steps": mismatches[path.stem][:20],
        }
        for path in CANDIDATES
    },
    "pass": all(not value for value in mismatches.values()),
}
(HERE / "preflight_identity.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
print(json.dumps(result, indent=2, sort_keys=True))
raise SystemExit(0 if result["pass"] else 1)
