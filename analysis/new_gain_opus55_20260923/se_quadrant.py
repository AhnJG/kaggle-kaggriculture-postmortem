"""What does each top team keep on the SE quadrant (x5-9, y5-9)? Read-only on raw replays."""
import json, collections
eps = json.load(open('analysis/top_agents_20260923/episodes.json'))
out = collections.defaultdict(lambda: collections.defaultdict(collections.Counter))
for ep in eps:
    if ep['team'] if False else ep['team_name'] not in ('DSM',): continue
    r = json.load(open(ep['replay_path'])); s = ep['seat']
    for d in (10, 12, 14, 16, 18, 20, 23, 26, 28):
        t = d * 24 + 23
        farm = r['steps'][t][s]['observation']['farms'][s]
        for y in range(5, 10):
            for x in range(5, 10):
                tile = farm['tiles'][y][x]
                if tile is None: k = 'EMPTY'
                elif isinstance(tile, str): k = tile
                elif tile.get('kind') == 'PLANT': k = 'PLANT:' + tile['crop']
                elif 'animal' in tile: k = 'ANIMAL:' + tile['animal']
                else: k = tile.get('kind')
                out[ep['team_name']][d][k] += 1
for team, days in out.items():
    for d, c in sorted(days.items()):
        print(team, 'day', d, {k: round(v / 40, 1) for k, v in c.most_common()})
