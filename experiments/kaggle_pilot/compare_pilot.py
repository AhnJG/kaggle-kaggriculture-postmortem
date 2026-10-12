"""python experiments/kaggle_pilot/compare_pilot.py  -> PASS/FAIL line. Needs out/games-pilot.jsonl, out/meta.json."""
import json
mac = {}
for l in open('experiments/exp030_dpnew_bypass/games-screen.jsonl'):
    r = json.loads(l); mac[r['key']] = r
kg = [json.loads(l) for l in open('experiments/kaggle_pilot/out/games-pilot.jsonl')]
meta = json.load(open('experiments/kaggle_pilot/out/meta.json'))
bad = [r['key'] for r in kg if (r['rewards'], r['act_sha'], r['action_count']) != (mac[r['key']]['rewards'], mac[r['key']]['act_sha'], mac[r['key']]['action_count'])]
err = [r['key'] for r in kg if r['err'] or r['agent_errors']]
sec_k = sum(r['sec'] for r in kg) / len(kg); sec_m = sum(mac[r['key']]['sec'] for r in kg) / len(kg)
ok = len(kg) == 60 and not bad and not err and meta['engine_sha'].startswith('bc8a5487')
gpm = 60 * len(kg) / meta['game_wall_sec']
print(('PASS' if ok else 'FAIL'), f"games={len(kg)} mismatch={len(bad)} errors={len(err)} cpu={meta['cpu_count']} "
      f"sec/game kaggle={sec_k:.1f} mac={sec_m:.1f} kaggle_games_per_min={gpm:.1f} engine={meta['engine_sha'][:8]}")
if bad: print('mismatch sample', bad[:5])
