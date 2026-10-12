from tools.postmortem_hosted import durable_loss_day, same_order_multiset, step_snapshot


def test_same_order_multiset_ignores_order_only():
    assert same_order_multiset(
        [["HIRE"], ["SELL", "MILK", 3]],
        [["SELL", "MILK", 3], ["HIRE"]],
    )
    assert not same_order_multiset([["SELL", "MILK", 3]], [["SELL", "MILK", 4]])


def test_durable_loss_day_requires_loss_to_stay_beyond_threshold():
    curve = [
        {"day": 0, "step": 23, "gap": -6000},
        {"day": 1, "step": 47, "gap": -1000},
        {"day": 2, "step": 71, "gap": -7000},
        {"day": 3, "step": 95, "gap": -8000},
    ]
    assert durable_loss_day(curve, 5000) == {
        "threshold": 5000,
        "day": 2,
        "step": 71,
        "gap": -7000,
    }


def test_step_snapshot_uses_target_observer_and_absolute_farm_seats():
    replay = {
        "info": {"TeamNames": ["opp", "Sian"]},
        "steps": [[
            {"action": {"market": []}, "observation": {}},
            {
                "action": {"market": [["HIRE"]]},
                "observation": {"farms": [
                    {"money": 52, "hands": [[1, 1]], "tiles": [[None]]},
                    {"money": 0, "hands": [], "tiles": [[{"crop": "WHEAT"}]]},
                ]},
            },
        ]],
    }
    assert step_snapshot(replay, "Sian", 0)["target"] == {
        "bank": 0,
        "hands": 0,
        "nonempty_tiles": 1,
        "action": {"market": [["HIRE"]]},
    }
