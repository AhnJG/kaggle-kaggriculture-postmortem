import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("mirror_edge_exp021_continue", ROOT / "tools/mirror_edge_exp021_continue.py")
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


def test_parent_step0_diagnostic_matches_frozen_fallback_condition():
    result = M.record_parent_step0()
    assert [row["action"]["market"] for row in result["rows"]] == [
        [["BUY_PRODUCT", "WHEAT", 5], ["BUY_SEED", "WHEAT", 1]],
        [["BUY_PRODUCT", "WHEAT", 5], ["BUY_SEED", "WHEAT", 1]],
    ]
    assert "_pipe_install" in result["reason_sell_absent"]


def test_h2_gate_is_frozen_stop_without_rerun():
    result = M.h2_stop()
    assert result["status"] == "STOP"
    assert result["games"] == result["invalid"] == 8
