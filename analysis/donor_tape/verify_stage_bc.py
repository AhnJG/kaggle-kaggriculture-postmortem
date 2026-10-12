import os
import json
import hashlib
import sys

OUTPUT_DIR = "analysis/donor_tape_20260919/stage_bc"
RAW_DIR = "private_artifacts/donor_tape_20260919/raw"

def get_sha256(data):
    if data is None:
        return None
    return hashlib.sha256(json.dumps(data, sort_keys=True, separators=(',',':')).encode('utf-8')).hexdigest()

def test_extract():
    from extract_stage_bc import get_market_nonempty_agree, get_sha256, extract_actions
    
    # Test market_nonempty_agree
    act1 = [
        {"farmer": ["PASS"], "market": [["SELL", "WHEAT", 1]]},
        {"farmer": ["PASS"], "market": []},
        {"farmer": ["PASS"], "market": None}
    ]
    act2 = [
        {"farmer": ["PASS"], "market": [["SELL", "WHEAT", 1]]},
        {"farmer": ["PASS"], "market": [["BUY_PRODUCT", "WHEAT", 1]]},
        {"farmer": ["PASS"], "market": []}
    ]
    agree = get_market_nonempty_agree(act1, act2)
    assert agree == 0.5, f"Expected 0.5, got {agree}"
    
    # Test seat identification and hashing
    fake_replay = {
        "info": {"TeamNames": ["A", "B"], "EpisodeId": 1},
        "rewards": [100, 200],
        "steps": [
            [{"action": {}}, {"action": {}}],
        ] + [[{"action": {"farmer": ["PASS"]}}, {"action": {"farmer": ["DO_SOMETHING"]}}]] * 719
    }
    
    res0 = extract_actions(fake_replay, 0, 1, 999, "A", 100)
    assert res0 != "identity_mismatch" and res0 != "length_mismatch"
    assert res0["seat"] == 0
    
    res1 = extract_actions(fake_replay, 1, 1, 999, "B", 200)
    assert res1 != "identity_mismatch"
    assert res1["seat"] == 1
    
    expected_full = get_sha256([{"farmer": ["PASS"]}] * 719)
    assert res0["full_sha"] == expected_full
    
    res_err = extract_actions(fake_replay, 0, 1, 999, "WrongName", 100)
    assert res_err == "identity_mismatch"
    print("Unit test passed.")

def verify():
    with open(os.path.join(OUTPUT_DIR, "summary.json")) as f:
        summary = json.load(f)
    total_downloads = summary["download_b"] + summary["download_c"]
    assert total_downloads <= 147, f"Too many downloads: {total_downloads}"
    
    # Verify download log entries = 87
    with open(os.path.join(OUTPUT_DIR, "download_log.json")) as f:
        dl_log = json.load(f)
    assert len(dl_log) == 87, f"Expected 87 entries in download log, got {len(dl_log)}"
    
    # Check 3 random pairs
    import random
    with open(os.path.join(OUTPUT_DIR, "stage_b_pairs.json")) as f:
        stage_b_pairs = json.load(f)
        
    teams = list(stage_b_pairs.keys())
    if len(teams) >= 3:
        sample_teams = random.sample(teams, 3)
    else:
        sample_teams = teams
        
    with open("analysis/donor_tape_20260919/selection_stageB.json") as f:
        sel_b = json.load(f)
        
    for tid in sample_teams:
        team_data = next(t for t in sel_b["selected_teams"] if str(t["team_id"]) == str(tid))
        target_sub = team_data["target_submission"]
        for ep in team_data["episodes"]:
            ep_id = ep["id"]
            
            seat = 0
            for ag in ep["agents"]:
                if ag["submissionId"] == target_sub:
                    seat = ag["index"]
            
            raw_path = os.path.join(RAW_DIR, f"episode-{ep_id}-replay.json")
            with open(raw_path) as f:
                replay = json.load(f)
                
            actions2 = []
            for t in range(1, len(replay["steps"])):
                if t >= 720: break
                actions2.append(replay["steps"][t][seat]["action"])
                
            hash2 = get_sha256(actions2)
            
            act_path = os.path.join(OUTPUT_DIR, "actions", f"{tid}-{ep_id}.json")
            with open(act_path) as f:
                act_data = json.load(f)
                
            assert act_data["full_sha"] == hash2, f"Hash mismatch for {tid}-{ep_id}"
            
    print("Verification passed.")

if __name__ == "__main__":
    test_extract()
    verify()
