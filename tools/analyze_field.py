import json

for ep in ['109856629', '110106409', '109831239', '109802471']:
    path = f"evidence/raw/p1c_replays/episode-{ep}-replay.json"
    with open(path) as f: r = json.load(f)
    seat = r['info']['TeamNames'].index('Sian')
    final_obs = r['steps'][-1][0]['observation']
    my_farm = final_obs['farms'][seat]
    
    ready_crops = []
    unready_crops = []
    for y, row in enumerate(my_farm['tiles']):
        for x, t in enumerate(row):
            if t and 'kind' in t and t['kind'] not in ['WEED', 'PASTURE', 'COOP']:
                if t.get('yield_units', 0) > 0:
                    ready_crops.append(t['kind'])
                else:
                    unready_crops.append(t['kind'])
    print(f"=== {ep} ===")
    print(f"Ready: {ready_crops}")
    print(f"Unready: {unready_crops}")
    print()
