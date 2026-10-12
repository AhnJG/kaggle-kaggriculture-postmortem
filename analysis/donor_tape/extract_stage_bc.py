import os
import json
import hashlib
import time
import sys
from kaggle.api.kaggle_api_extended import KaggleApi

RAW_DIR = "private_artifacts/donor_tape_20260919/raw"
OUTPUT_DIR = "analysis/donor_tape_20260919/stage_bc"
ACTIONS_DIR = os.path.join(OUTPUT_DIR, "actions")

os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(ACTIONS_DIR, exist_ok=True)

api = KaggleApi()
api.authenticate()

download_log_dict = {}
file_hashes = {}
summary = {
    "download_b": 0,
    "download_c": 0,
    "full_match_teams": 0,
    "field_match_teams": 0,
    "identity_length_issues": 0,
    "non_1_32_7_count": 0
}

def get_sha256(data):
    if data is None:
        return None
    return hashlib.sha256(json.dumps(data, sort_keys=True, separators=(',',':')).encode('utf-8')).hexdigest()

def get_file_sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def record_file_hash(path):
    if os.path.exists(path):
        file_hashes[os.path.basename(path)] = get_file_sha256(path)

def download_episode(episode_id, stage="B"):
    filename = f"{RAW_DIR}/episode-{episode_id}-replay.json"
    if not os.path.exists(filename):
        print(f"Downloading {episode_id} (Stage {stage})...")
        for attempt in range(10):
            try:
                api.competition_episode_replay(episode_id, path=RAW_DIR, quiet=True)
                download_log_dict[episode_id] = {
                    "episode_id": episode_id,
                    "timestamp": time.time(),
                    "result": "success",
                    "retries": attempt,
                    "bytes": os.path.getsize(filename),
                    "sha256": get_file_sha256(filename)
                }
                if stage == "B":
                    summary["download_b"] += 1
                else:
                    summary["download_c"] += 1
                return filename
            except Exception as e:
                if '429' in str(e) or 'Too Many Requests' in str(e):
                    time.sleep(10)
                else:
                    raise e
        raise Exception(f"BLOCKED: Failed to download {episode_id}")
    else:
        if episode_id not in download_log_dict:
            download_log_dict[episode_id] = {
                "episode_id": episode_id,
                "timestamp": time.time(),
                "result": "cached",
                "retries": 0,
                "bytes": os.path.getsize(filename),
                "sha256": get_file_sha256(filename)
            }
        return filename

def get_market_nonempty_agree(act1, act2):
    denom = 0
    num = 0
    for a1, a2 in zip(act1, act2):
        m1 = a1.get("market", [])
        m2 = a2.get("market", [])
        if m1 is None: m1 = []
        if m2 is None: m2 = []
        if len(m1) > 0 or len(m2) > 0:
            denom += 1
            if m1 == m2:
                num += 1
    if denom == 0:
        return None
    return num / denom

def get_first_diff_index(act1, act2):
    for i, (a1, a2) in enumerate(zip(act1, act2)):
        if a1 != a2:
            return i
    return None

def process_episode(episode_id, expected_team_name, expected_reward, target_submission, stage="B"):
    path = download_episode(episode_id, stage)
    with open(path, 'r') as f:
        replay = json.load(f)
    
    info = replay.get('info', {})
    if info.get('EpisodeId') != episode_id:
        print(f"Warning: EpisodeId mismatch in {episode_id}")
        
    module_version = replay.get('module_version')
    if module_version != '1.32.7':
        summary["non_1_32_7_count"] += 1

    if episode_id in download_log_dict:
        download_log_dict[episode_id]["module_version"] = module_version
        download_log_dict[episode_id]["configuration"] = replay.get("configuration")
        download_log_dict[episode_id]["rewards"] = replay.get("rewards")
        
    return replay

def extract_actions(replay, seat, episode_id, team_id, expected_team_name, expected_reward):
    info = replay.get('info', {})
    team_names = info.get('TeamNames', [])
    rewards = replay.get('rewards', [])
    
    identity_mismatch = False
    if len(team_names) > seat and team_names[seat] != expected_team_name:
        identity_mismatch = True
    if len(rewards) > seat and rewards[seat] != expected_reward:
        identity_mismatch = True
        
    if identity_mismatch:
        return "identity_mismatch"
        
    steps = replay.get('steps', [])
    actions = []
    
    for t in range(1, min(720, len(steps))):
        step_data = steps[t][seat]
        if 'action' not in step_data:
            print(f"BLOCKED: action missing at step {t} seat {seat} in episode {episode_id}")
            sys.exit(1)
        actions.append(step_data['action'])
        
    if len(actions) != 719:
        return "length_mismatch"
        
    full_sha = get_sha256(actions)
    field_actions = [{"farmer": a.get("farmer"), "hands": a.get("hands")} for a in actions]
    field_sha = get_sha256(field_actions)
    market_actions = [{"market": a.get("market")} for a in actions]
    market_sha = get_sha256(market_actions)
    
    res = {
        "actions": actions,
        "seat": seat,
        "full_sha": full_sha,
        "field_sha": field_sha,
        "market_sha": market_sha
    }
    
    out_path = os.path.join(ACTIONS_DIR, f"{team_id}-{episode_id}.json")
    with open(out_path, 'w') as f:
        json.dump(res, f)
        
    return res

def main():
    with open("analysis/donor_tape_20260919/selection_stageB.json", "r") as f:
        sel_b = json.load(f)
        
    stage_b_episodes = set()
    for team in sel_b["selected_teams"]:
        for ep in team["episodes"]:
            stage_b_episodes.add(ep["id"])
            
    if len(stage_b_episodes) != 87:
        print(f"BLOCKED: Unique Stage B episodes is {len(stage_b_episodes)}, expected 87.")
        sys.exit(1)
        
    stage_b_pairs = {}
    full_match_teams = []
    identity_mismatch_count = 0
    
    for team in sel_b["selected_teams"]:
        team_id = team["team_id"]
        target_sub = team["target_submission"]
        
        team_results = []
        skip_team = False
        
        for ep in team["episodes"]:
            ep_id = ep["id"]
            
            seat = 0
            expected_team_name = ""
            expected_reward = 0
            for ag in ep["agents"]:
                if ag["submissionId"] == target_sub:
                    seat = ag["index"]
                    expected_team_name = ag["teamName"]
                    expected_reward = ag["reward"]
                    break
            
            replay = process_episode(ep_id, expected_team_name, expected_reward, target_sub, stage="B")
            ext = extract_actions(replay, seat, ep_id, team_id, expected_team_name, expected_reward)
            
            if ext == "identity_mismatch":
                identity_mismatch_count += 1
                summary["identity_length_issues"] += 1
                skip_team = True
                break
            elif ext == "length_mismatch":
                summary["identity_length_issues"] += 1
                skip_team = True
                break
            else:
                team_results.append(ext)
                
        if identity_mismatch_count >= 10:
            print("BLOCKED: identity_mismatch >= 10")
            sys.exit(1)
            
        if not skip_team and len(team_results) == 2:
            act1 = team_results[0]["actions"]
            act2 = team_results[1]["actions"]
            
            full_match = team_results[0]["full_sha"] == team_results[1]["full_sha"]
            field_match = team_results[0]["field_sha"] == team_results[1]["field_sha"]
            m_agree = get_market_nonempty_agree(act1, act2)
            first_diff = get_first_diff_index(act1, act2)
            
            stage_b_pairs[str(team_id)] = {
                "full_match": full_match,
                "field_match": field_match,
                "market_nonempty_agree": m_agree,
                "first_diff_index": first_diff
            }
            
            if full_match:
                summary["full_match_teams"] += 1
                full_match_teams.append({
                    "team_id": team_id,
                    "rank": team.get("rank", 999),
                    "target_sub": target_sub
                })
            if field_match:
                summary["field_match_teams"] += 1
                
    with open(os.path.join(OUTPUT_DIR, "stage_b_pairs.json"), "w") as f:
        json.dump(stage_b_pairs, f, indent=2)
        
    full_match_teams.sort(key=lambda x: x["rank"])
    
    stage_c_target_teams = full_match_teams[:15]
    overflow = [t["team_id"] for t in full_match_teams[15:]]
    
    with open("analysis/donor_tape_20260919/inventory.json", "r") as f:
        inventory = json.load(f)
        
    stage_c_selection = {
        "target_teams": [t["team_id"] for t in stage_c_target_teams],
        "overflow": overflow,
        "episodes_to_download": []
    }
    
    inv_map = {t["team_id"]: t for t in inventory["teams"]}
    
    for tt in stage_c_target_teams:
        tid = tt["team_id"]
        if tid in inv_map:
            inv_team = inv_map[tid]
            for ep in inv_team["episodes_window"]:
                if ep["id"] not in stage_b_episodes:
                    stage_c_selection["episodes_to_download"].append({
                        "team_id": tid,
                        "episode_id": ep["id"],
                        "target_sub": tt["target_sub"]
                    })
                    
    with open(os.path.join(OUTPUT_DIR, "stage_c_selection.json"), "w") as f:
        json.dump(stage_c_selection, f, indent=2)
        
    if len(full_match_teams) == 0:
        print("0 full_match teams. Skipping Stage C downloads.")
        stage_c_windows = {}
    else:
        stage_c_windows = {}
        for item in stage_c_selection["episodes_to_download"]:
            tid = item["team_id"]
            ep_id = item["episode_id"]
            target_sub = item["target_sub"]
            
            inv_team = inv_map[tid]
            expected_team_name = ""
            expected_reward = 0
            seat = 0
            for window_ep in inv_team["episodes_window"]:
                if window_ep["id"] == ep_id:
                    for ag in window_ep["agents"]:
                        if ag["submissionId"] == target_sub:
                            seat = ag["index"]
                            expected_team_name = ag["teamName"]
                            expected_reward = ag["reward"]
                            break
                    break
                    
            replay = process_episode(ep_id, expected_team_name, expected_reward, target_sub, stage="C")
            ext = extract_actions(replay, seat, ep_id, tid, expected_team_name, expected_reward)
            
        for tt in stage_c_target_teams:
            tid = tt["team_id"]
            inv_team = inv_map[tid]
            
            full_shas = []
            field_shas = []
            market_shas = []
            opponents = []
            donor_seats = []
            
            for ep in inv_team["episodes_window"]:
                ep_id = ep["id"]
                
                seat = 0
                opp = None
                for ag in ep["agents"]:
                    if ag["submissionId"] == tt["target_sub"]:
                        seat = ag["index"]
                    else:
                        opp = ag["teamId"]
                opponents.append(opp)
                donor_seats.append(seat)
                
                act_file = os.path.join(ACTIONS_DIR, f"{tid}-{ep_id}.json")
                if os.path.exists(act_file):
                    with open(act_file, "r") as f:
                        act_data = json.load(f)
                    full_shas.append(act_data["full_sha"])
                    field_shas.append(act_data["field_sha"])
                    market_shas.append(act_data["market_sha"])
                else:
                    full_shas.append(None)
                    field_shas.append(None)
                    market_shas.append(None)
                    
            valid_shas = [s for s in full_shas if s is not None]
            if len(valid_shas) > 0:
                mode_sha = max(set(valid_shas), key=valid_shas.count)
                k_of_6 = full_shas.count(mode_sha)
            else:
                k_of_6 = 0
                
            stage_c_windows[str(tid)] = {
                "full_shas": full_shas,
                "field_shas": field_shas,
                "market_shas": market_shas,
                "k_of_6": k_of_6,
                "opponents": opponents,
                "donor_seats": donor_seats
            }
            
    with open(os.path.join(OUTPUT_DIR, "stage_c_windows.json"), "w") as f:
        json.dump(stage_c_windows, f, indent=2)
        
    with open(os.path.join(OUTPUT_DIR, "download_log.json"), "w") as f:
        json.dump(list(download_log_dict.values()), f, indent=2)
        
    with open(os.path.join(OUTPUT_DIR, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
        
    record_file_hash(os.path.join(OUTPUT_DIR, "download_log.json"))
    record_file_hash(os.path.join(OUTPUT_DIR, "stage_b_pairs.json"))
    record_file_hash(os.path.join(OUTPUT_DIR, "stage_c_selection.json"))
    record_file_hash(os.path.join(OUTPUT_DIR, "stage_c_windows.json"))
    record_file_hash(os.path.join(OUTPUT_DIR, "summary.json"))
    
    for f_name in os.listdir(ACTIONS_DIR):
        if f_name.endswith(".json"):
            file_hashes[f"actions/{f_name}"] = get_file_sha256(os.path.join(ACTIONS_DIR, f_name))
    
    with open(os.path.join(OUTPUT_DIR, "file_hashes.json"), "w") as f:
        json.dump(file_hashes, f, indent=2)
        
    print("Done!")

if __name__ == "__main__":
    main()
