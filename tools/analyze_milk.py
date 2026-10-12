import json

path = "evidence/raw/p1c_replays/episode-110106409-replay.json"
with open(path) as f: r = json.load(f)
seat = r['info']['TeamNames'].index('Sian')

for i in range(715, 720):
    pre_obs = r['steps'][i-1][0]['observation']
    my_farm = pre_obs['farms'][seat]
    shed = r['steps'][i-1][seat]['observation']['private']['shed']
    action = r['steps'][i][seat].get('action', {})
    
    print(f"Step {i}:")
    print(f"Shed before action: {shed}")
    print(f"Action: farmer={action.get('farmer')}, hands={action.get('hands')}, market={action.get('market')}")
    
    # let's look at the tiles around the shed to see if MILK is on the ground
    # actually let's just see post-action state
    post_obs = r['steps'][i][0]['observation']
    post_shed = r['steps'][i][seat]['observation']['private']['shed']
    print(f"Shed after action: {post_shed}")
    
    # Did we get money from MILK?
    my_money_before = pre_obs['farms'][seat]['money']
    my_money_after = post_obs['farms'][seat]['money']
    print(f"Money change: {my_money_after - my_money_before}")
    print()
