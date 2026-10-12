import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("mirror_edge_exp021_v2", ROOT / "tools/mirror_edge_exp021_v2.py")
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


def test_v2_freeze_has_only_approved_four_arms():
    frozen = M.verify_v2()
    assert set(frozen["inputs"]["arms"]) == {"H1a", "H1b", "H3", "H4"}
    assert frozen["stage2"]["primary_o"]["pass"].startswith("Wilson 99%")
    assert frozen["preservation"]["existing_games"].startswith("Keep all 12")


def test_h2prime_wrapper_preserves_parent_and_entrypoint():
    item = M.prepare_h2prime()
    parent = (ROOT / M.B.PARENT).read_bytes()
    content = (ROOT / item["path"]).read_bytes()
    assert content.startswith(parent)
    from kaggle_environments.agent import get_last_callable
    assert get_last_callable(content.decode(), path=item["path"]).__name__ == "mirror_edge_h2prime_entry"


def test_gate_public_files_are_frozen_guard_top_two_excluding_anchors():
    frozen = json.loads(M.V2.read_text())
    paths = [item["path"] for item in frozen["inputs"]["public_guard_15"]
             if item["path"] not in (M.B.OPPONENT, M.B.DP)]
    assert tuple(paths[:2]) == M.PUBLIC_GATE_TWO
