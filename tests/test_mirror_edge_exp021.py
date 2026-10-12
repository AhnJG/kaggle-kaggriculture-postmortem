import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("mirror_edge_exp021", ROOT / "tools/mirror_edge_exp021.py")
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


def test_preregistration_has_frozen_scope():
    frozen = json.loads(M.PREREG.read_text())
    assert set(frozen["arms"]) == {"H1a", "H1b", "H2", "H3", "H4"}
    assert frozen["workers"] == 5
    assert len(frozen["inputs"]["public_guard_15"]) == 15
    assert frozen["stages"]["stage1"]["total_games"] == 600
    assert frozen["stages"]["final_confirmation"]["seeds"] == [5600, 5799]


def test_variants_preserve_parent_prefix_and_are_callable():
    variants = M.prepare_variants()
    parent = (ROOT / M.PARENT).read_bytes()
    from kaggle_environments.agent import get_last_callable
    for arm, item in variants.items():
        content = (ROOT / item["path"]).read_bytes()
        assert content.startswith(parent)
        assert content != parent
        function = get_last_callable(content.decode(), path=item["path"])
        assert function.__name__ == "mirror_edge_entry", arm


def test_candidate_valid_ignores_only_opponent_caught_counters():
    base = {"steps": 720, "statuses": ["DONE", "DONE"], "exceptions": [[], []],
            "caught_errors": {"candidate": [], "opponent": [{"counter": "x.errors", "value": 1}]}}
    assert M.candidate_valid(base)
    bad = json.loads(json.dumps(base))
    bad["caught_errors"]["candidate"] = [{"counter": "x.errors", "value": 1}]
    assert not M.candidate_valid(bad)
