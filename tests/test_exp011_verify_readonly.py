"""Regression: live provenance drift must never overwrite frozen measurements."""
import hashlib
import importlib.util
from pathlib import Path

PATH = Path('experiments/results/p1_shed_attribution/run.py')


def load():
    spec = importlib.util.spec_from_file_location('exp011_verifier', PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_verification_never_writes_for_success_or_identity_failure(monkeypatch):
    module = load()
    protected = ['aggregate.json', 'freeze.json', 'commands.json', 'allocation_audit.json']
    before = {p: hashlib.sha256((module.ROOT/p).read_bytes()).hexdigest() for p in protected}
    def reject_write(*args):
        raise AssertionError('verify-only attempted a write')
    monkeypatch.setattr(module, 'write', reject_write)
    # Controlled identity outcome tests verifier behavior without mutating freeze or files.
    monkeypatch.setattr(module, 'identity', lambda: [])
    assert module.verify() == 0
    monkeypatch.setattr(module, 'identity', lambda: [{'path':'card', 'expected':'old', 'actual':'new'}])
    assert module.verify() == 1
    assert before == {p: hashlib.sha256((module.ROOT/p).read_bytes()).hexdigest() for p in protected}
