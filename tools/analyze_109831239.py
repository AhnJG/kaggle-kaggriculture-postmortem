import json

ep = '109831239'
path = f"evidence/raw/p1c_replays/episode-{ep}-replay.json"
with open(path) as f: r = json.load(f)
seat = r['info']['TeamNames'].index('Sian')

for i in range(716, 720):
    obs = r['steps'][i-1][0]['observation']
    market_prices = obs['market']['prices']
    my_money = obs['farms'][seat]['money']
    action = r['steps'][i][seat].get('action', {})
    print(f"Step {i}: Money={my_money}, Prices={market_prices}")
    print(f"Market Action: {action.get('market')}")
    print(f"Farmer: {action.get('farmer')}, Hands: {action.get('hands')}")
    print()
