import json, sys, time
import instr
out = open(sys.argv[2], 'w')
n = 0
for line in open(sys.argv[1]):
    rec = json.loads(line)
    if len(sys.argv) > 3 and n >= int(sys.argv[3]): break
    n += 1
    t0 = time.time()
    acts = rec['actions']
    r = instr.run([instr.tape_agent(acts, 0), instr.tape_agent(acts, 1)], rec['seed'])
    hosted_shops = rec['shops_by_day']
    match_shops = all(r['shops'].get(int(d), []) == v for d, v in hosted_shops.items() if int(d) > 0)
    r.update(episode_id=rec['episode_id'], team=rec['team'], seat=rec['seat'], opponent=rec['opponent'],
             hosted_rewards=rec['rewards'], reward_match=[abs(a - b) < 1e-6 for a, b in zip(r['rewards'], rec['rewards'])],
             shops_match=match_shops, secs=round(time.time() - t0, 2))
    out.write(json.dumps(r) + '\n'); out.flush()
    print(rec['episode_id'], rec['team'], r['rewards'], rec['rewards'], r['reward_match'], match_shops, r['secs'], flush=True)
