import os
import json
import time
from kaggle_environments import make, agent

BOT_X_PATH = 'releases/public-ahmedberatozer-kaggriculture-v56-smarter-seeds-and-fertilizer-exact/main.py'
EXP016_PATH = 'releases/f0-c1-adv-exp016/main.py'
EXP017_PATH = 'releases/f0-omw-adv-exp017/main.py'

SEEDS = list(range(2300, 2310))

def run_match_pair(bot_x_callable, opp_callable, opp_name):
    print(f"\n=================== RUNNING ARENA: X vs {opp_name} ===================")
    results = []
    step_times = []
    
    # Timing wrapper for Bot X
    def x_wrapper(obs, config=None):
        t0 = time.perf_counter()
        act = bot_x_callable(obs, config)
        t1 = time.perf_counter()
        step_times.append(t1 - t0)
        return act

    for seed in SEEDS:
        # Match 1: X = Seat 0, Opp = Seat 1
        env1 = make('kaggriculture', configuration={'episodeSteps': 720, 'seed': seed})
        env1.run([x_wrapper, opp_callable])
        
        status0 = env1.steps[-1][0].get('status', 'DONE')
        status1 = env1.steps[-1][1].get('status', 'DONE')
        rew0 = env1.steps[-1][0].get('reward', 0)
        rew1 = env1.steps[-1][1].get('reward', 0)
        margin0 = rew0 - rew1
        
        err0 = (status0 == 'ERROR')
        err1 = (status1 == 'ERROR')
        
        if rew0 > rew1:
            res0 = 'W'
        elif rew0 < rew1:
            res0 = 'L'
        else:
            res0 = 'D'
            
        results.append({
            'seed': seed,
            'x_seat': 0,
            'res': res0,
            'margin': margin0,
            'rew_x': rew0,
            'rew_opp': rew1,
            'err_x': err0,
            'err_opp': err1
        })
        print(f"Seed {seed} (Seat 0): {res0} | Margin: {margin0:+.0f} (X: {rew0:.0f}, Opp: {rew1:.0f})")
        
        # Match 2: X = Seat 1, Opp = Seat 0
        env2 = make('kaggriculture', configuration={'episodeSteps': 720, 'seed': seed})
        env2.run([opp_callable, x_wrapper])
        
        status0 = env2.steps[-1][0].get('status', 'DONE')
        status1 = env2.steps[-1][1].get('status', 'DONE')
        rew0 = env2.steps[-1][0].get('reward', 0)
        rew1 = env2.steps[-1][1].get('reward', 0)
        margin1 = rew1 - rew0
        
        err0 = (status0 == 'ERROR')
        err1 = (status1 == 'ERROR')
        
        if rew1 > rew0:
            res1 = 'W'
        elif rew1 < rew0:
            res1 = 'L'
        else:
            res1 = 'D'
            
        results.append({
            'seed': seed,
            'x_seat': 1,
            'res': res1,
            'margin': margin1,
            'rew_x': rew1,
            'rew_opp': rew0,
            'err_x': err1,
            'err_opp': err0
        })
        print(f"Seed {seed} (Seat 1): {res1} | Margin: {margin1:+.0f} (X: {rew1:.0f}, Opp: {rew0:.0f})")

    # Aggregate stats
    w = sum(1 for r in results if r['res'] == 'W')
    d = sum(1 for r in results if r['res'] == 'D')
    l = sum(1 for r in results if r['res'] == 'L')
    margins = [r['margin'] for r in results]
    mean_margin = sum(margins) / len(margins)
    worst_margin = min(margins)
    exceptions = sum(1 for r in results if r['err_x'])
    max_step_time = max(step_times) if step_times else 0.0

    print(f"\n--- Summary for X vs {opp_name} (20 matches) ---")
    print(f"W/D/L: {w}/{d}/{l}")
    print(f"Mean Margin: {mean_margin:+.1f}")
    print(f"Worst Margin: {worst_margin:+.0f}")
    print(f"Exceptions: {exceptions}")
    print(f"Max Step Time: {max_step_time:.4f}s")
    
    return {
        'opponent': opp_name,
        'w': w,
        'd': d,
        'l': l,
        'mean_margin': mean_margin,
        'worst_margin': worst_margin,
        'exceptions': exceptions,
        'max_step_time': max_step_time,
        'matches': results
    }

def main():
    with open(BOT_X_PATH) as f:
        fn_x = agent.get_last_callable(f.read(), path=BOT_X_PATH)
    with open(EXP016_PATH) as f:
        fn_exp016 = agent.get_last_callable(f.read(), path=EXP016_PATH)
    with open(EXP017_PATH) as f:
        fn_exp017 = agent.get_last_callable(f.read(), path=EXP017_PATH)

    res_016 = run_match_pair(fn_x, fn_exp016, 'EXP-016')
    res_017 = run_match_pair(fn_x, fn_exp017, 'EXP-017')
    
    out_path = 'analysis/step91_id/arena_results.json'
    with open(out_path, 'w') as f:
        json.dump({'x_vs_exp016': res_016, 'x_vs_exp017': res_017}, f, indent=2)
    print(f"\nSaved all arena results to {out_path}")

if __name__ == '__main__':
    main()
