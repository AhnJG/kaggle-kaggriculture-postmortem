import json, sys

def analyze(episode_id):
    path = f"evidence/raw/p1c_replays/episode-{episode_id}-replay.json"
    with open(path) as f: r = json.load(f)
    names = r['info']['TeamNames']
    seat = names.index('Sian')
    print(f"=== {episode_id} ===")
    
    for i in range(len(r['steps'])-5, len(r['steps'])):
        if i <= 0: continue
        pre_state = r['steps'][i-1][0]['observation']
        action = r['steps'][i][seat].get('action', {})
        my_farm = pre_state['farms'][seat]
        my_money = my_farm['money']
        my_inv = pre_state['private']['inventories'][seat]
        print(f"Step {i}: Money={my_money}, Inv={my_inv}")
        print(f"Action: {action}")
    print()

for ep in ['109856629', '110106409', '109831239', '109802471']:
    analyze(ep)
