import json

for ep in ['109856629', '110106409', '109831239', '109802471']:
    path = f"evidence/raw/p1c_replays/episode-{ep}-replay.json"
    with open(path) as f: r = json.load(f)
    seat = r['info']['TeamNames'].index('Sian')
    print(f"=== {ep} (My Seat: {seat}) ===")
    
    # We want to see what is unsold right before the last step (Step 719 starts)
    # Wait, the final reward is evaluated after step 719 finishes. 
    # Let's see the state at step 720 (index -1)
    final_obs = r['steps'][-1][seat]['observation']
    my_farm = final_obs['farms'][seat]
    
    shed = final_obs['private']['shed']
    invs = final_obs['private']['inventories']
    
    held = {}
    for inv in invs:
        for k, v in inv.items():
            if v > 0:
                held[k] = held.get(k, 0) + v
                
    print(f"Final Shed: {shed}")
    print(f"Final Held in Hands/Farmer: {held}")
    print()
