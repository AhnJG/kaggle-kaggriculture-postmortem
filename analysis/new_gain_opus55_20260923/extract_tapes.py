"""Extract compact (seed, both-seat actions, hosted shops/rewards) from top-agent replays.
Read-only on raw replays. Output: private_artifacts/new_gain_opus55_20260923/tapes.jsonl"""
import json, hashlib
from pathlib import Path
eps = json.load(open('analysis/top_agents_20260923/episodes.json'))
out = open('private_artifacts/new_gain_opus55_20260923/tapes.jsonl', 'w')
for ep in eps:
    p = Path(ep['replay_path']); raw = p.read_bytes(); r = json.loads(raw)
    s = r['steps']
    acts = [[s[t][k].get('action') for k in (0, 1)] for t in range(len(s))]
    shops_by_day = {}
    for t in range(0, len(s), 24):
        shops_by_day[t // 24] = list(s[t][0]['observation'].get('town', {}).get('unlocked_shops', []))
    rec = dict(episode_id=ep['episode_id'], team=ep['team_name'], seat=ep['seat'], opponent=ep['opponent'],
               seed=r['info']['seed'], names=r['info']['TeamNames'], rewards=r['rewards'], statuses=r['statuses'],
               nsteps=len(s), shops_by_day=shops_by_day, actions=acts,
               replay_sha256=hashlib.sha256(raw).hexdigest())
    out.write(json.dumps(rec) + '\n')
out.close(); print('ok', len(eps))
