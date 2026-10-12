import json

for ep in ['109856629', '110106409', '109831239', '109802471']:
    path = f"evidence/raw/p1c_replays/episode-{ep}-replay.json"
    with open(path) as f: r = json.load(f)
    seat = r['info']['TeamNames'].index('Sian')
    print(f"=== {ep} ===")
    final_obs = r['steps'][-1][0]['observation']
    final_private = r['steps'][-1][seat]['observation']['private']
    my_farm = final_obs['farms'][seat]
    
    shed = final_private.get('shed', {})
    invs = final_private.get('inventories', [])
    
    held = {}
    for inv in invs:
        for k, v in inv.items():
            if v > 0:
                held[k] = held.get(k, 0) + v
                
    tiles = my_farm.get('tiles', [])
    crops = {}
    for row in tiles:
        for t in row:
            if t and 'kind' in t and t['kind'] not in ['WEED', 'PASTURE', 'COOP'] and t.get('yield_units', 0) > 0:
                kind = t['kind']
                crops[kind] = crops.get(kind, 0) + 1
                
    print(f"Shed remaining: {shed}")
    print(f"Hands remaining: {held}")
    print(f"Ready crops: {crops}")
    
    # print market prices at step 719
    market_prices = final_obs['market']['prices']
    
    # sum values
    shed_val = sum(market_prices.get(k, 0) * v for k, v in shed.items())
    held_val = sum(market_prices.get(k, 0) * v for k, v in held.items())
    crop_val = sum(market_prices.get(k, 0) * v for k, v in crops.items())
    
    print(f"Values -> Shed: {shed_val}, Hands: {held_val}, Crops: {crop_val}")
    print()
