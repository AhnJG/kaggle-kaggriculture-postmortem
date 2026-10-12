import json

for ep in ['109856629', '110106409', '109831239', '109802471']:
    path = f"evidence/raw/p1c_replays/episode-{ep}-replay.json"
    with open(path) as f: r = json.load(f)
    seat = r['info']['TeamNames'].index('Sian')
    final_obs = r['steps'][-1][0]['observation']
    my_farm = final_obs['farms'][seat]
    
    animals = []
    for y, row in enumerate(my_farm['tiles']):
        for x, t in enumerate(row):
            if t and 'animal' in t:
                animals.append((t['animal'], t.get('yield_units', 0)))
    print(f"=== {ep} ===")
    print(f"Animals: {animals}")
    print()
