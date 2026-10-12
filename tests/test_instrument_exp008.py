from types import SimpleNamespace

from tools.instrument import (
    _tape_agent,
    action_difference,
    action_stream_sha256,
    instrumented_run,
    local_step_snapshot,
    seed_blocked_plants,
)
from tools.verify_pool import pool_sha256


def test_seed_blocked_plants_matches_atomic_engine_rule():
    action = {
        "farmer": ["PLANT", "WHEAT"],
        "hands": [["PLANT", "WHEAT"], ["PLANT", "CARROT"]],
        "market": [],
    }
    assert seed_blocked_plants(action, {"WHEAT": 1, "CARROT": 1}) == {"WHEAT": 2}


def test_local_step_snapshot_reads_stored_observation_index():
    farms = [
        {"money": 4, "hands": [[1, 1]], "tiles": [[None, {"crop": "WHEAT"}]]},
        {"money": 7, "hands": [], "tiles": [[{}, None]]},
    ]
    states = [
        SimpleNamespace(observation={"farms": farms}, action={"market": [["HIRE"]]}),
        SimpleNamespace(observation={}, action={"market": []}),
    ]
    snapshot = local_step_snapshot([states], 0)
    assert snapshot["players"][0] == {
        "seat": 0,
        "bank": 4,
        "hands": 1,
        "nonempty_tiles": 1,
        "action": {"market": [["HIRE"]]},
    }
    assert snapshot["players"][1]["nonempty_tiles"] == 1


def test_action_difference_separates_market_from_unit_changes():
    left = [
        {"step": 1, "action": {"farmer": ["PASS"], "hands": [], "market": [["BUY", 1]]}},
        {"step": 2, "action": {"farmer": ["PASS"], "hands": [], "market": []}},
    ]
    right = [
        {"step": 1, "action": {"farmer": ["PASS"], "hands": [], "market": [["SELL", 1]]}},
        {"step": 2, "action": {"farmer": ["NORTH"], "hands": [], "market": []}},
    ]
    assert action_difference(left, right) == {
        "different_steps": [1, 2],
        "farmer_or_hands_different_steps": [2],
        "market_different_steps": [1],
    }
    assert action_stream_sha256(left) != action_stream_sha256(right)


def test_pool_sha256_is_filename_and_input_order_independent(tmp_path):
    left = tmp_path / "z.json"
    right = tmp_path / "a.json"
    left.write_text("left", encoding="utf-8")
    right.write_text("right", encoding="utf-8")
    assert pool_sha256([left, right]) == pool_sha256([right, left])


def test_tape_agent_rejects_noncontiguous_turns(tmp_path):
    tape = tmp_path / "bad.json"
    tape.write_text(
        '[{"turn": 0, "action": {}}, {"turn": 2, "action": {}}]', encoding="utf-8"
    )
    try:
        _tape_agent(tape)
    except ValueError as exc:
        assert "index 1" in str(exc)
    else:
        raise AssertionError("noncontiguous tape was accepted")


def test_engine_run_attributes_hire_and_seed_failures_to_each_player():
    def failing_agent(obs, config=None):
        crop = next(name for name, count in obs["private"]["seeds"].items() if not count)
        return {
            "farmer": ["PLANT", crop],
            "hands": [],
            "market": [["HIRE"]] * 10,
        }

    report = instrumented_run(
        [failing_agent, failing_agent], seed=7, episode_steps=12, capture_actions=True
    )
    assert [counter.seed_blocked_plant for counter in report.players] == [11, 11]
    assert all(counter.hire_failed > 0 for counter in report.players)
    assert [len(stream) for stream in report.action_streams] == [11, 11]


def test_instrument_records_hands_length_mismatch_as_gate_failure():
    def mismatched_agent(obs, config=None):
        return {"farmer": ["PASS"], "hands": [["PASS"]], "market": []}

    report = instrumented_run([mismatched_agent, mismatched_agent], seed=7, episode_steps=3)
    assert [counter.hands_length_mismatch_count for counter in report.players] == [2, 2]
    assert not any(counter.is_clean() for counter in report.players)


def test_instrument_records_first_call_and_both_player_timing():
    def clean_agent(obs, config=None):
        player = int(obs["player"])
        hands = [["PASS"] for _ in (obs["farms"][player].get("hands") or [])]
        return {"farmer": ["PASS"], "hands": hands, "market": []}

    report = instrumented_run(
        [clean_agent, clean_agent], seed=7, episode_steps=3, time_agent_indices=(0, 1)
    )
    assert len(report.agent_ms_by_player) == 2
    for timing in report.agent_ms_by_player:
        assert timing["n"] == 2
        assert timing["first_call_ms"] >= 0
        assert timing["total_s"] >= 0
    assert report.combined_agent_cpu_seconds == sum(
        timing["total_s"] for timing in report.agent_ms_by_player
    )
