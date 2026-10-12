import json
import random
import os

manifest_path = 'analysis/p2_losses_20260920/manifest.json'
with open(manifest_path, 'r') as f:
    manifest = json.load(f)
    
if len(manifest) == 0:
    print("Manifest is empty.")
    exit(0)
    
sample = random.sample(manifest, min(3, len(manifest)))

for item in sample:
    path = item['path']
    ep_id = item['id']
    seat = item['seat']
    expected_result = item['result']
    
    with open(path, 'r') as f:
        data = json.load(f)
        
    team_names = data['info'].get('TeamNames') or []
    actual_seat_name = team_names[seat] if len(team_names) > seat else "Unknown"
    rewards = data.get('rewards', [])
    if len(rewards) == 0 and 'steps' in data:
        # Fallback if top-level rewards is missing
        last_step = data['steps'][-1]
        rewards = [agent['reward'] for agent in last_step]
        
    actual_reward = rewards[seat]
    op_seat = 1 if seat == 0 else 0
    op_reward = rewards[op_seat]
    
    actual_res = 'D'
    if actual_reward > op_reward: actual_res = 'W'
    elif actual_reward < op_reward: actual_res = 'L'
    
    print(f"[{ep_id}] File: {path}")
    print(f"  Expected Seat: {seat}, Actual Seat Name: {actual_seat_name}")
    print(f"  Expected Result: {expected_result}, Actual Result: {actual_res}")
    print(f"  Rewards: {rewards}")
    
    assert actual_seat_name == 'Sian', f"Mismatch seat name: {actual_seat_name}"
    assert actual_res == expected_result, f"Mismatch result: expected {expected_result}, got {actual_res}"

print("Verification passed.")
