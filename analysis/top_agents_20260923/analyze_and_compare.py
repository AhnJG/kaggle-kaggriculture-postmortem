import json
import os
import sys
from pathlib import Path
from kaggle_environments import make

EPISODES_JSON = Path("analysis/top_agents_20260923/episodes.json")
OUTPUT_STATS_JSON = Path("analysis/top_agents_20260923/stats_summary.json")

CANDIDATE_PATH = "releases/f0-omw-adv-exp017/main.py"
PARENT_PATH = "releases/public-dmitriigluzdov-kaggriculture-one-more-wheat-exact/main.py"

ANIMAL_KEYS = ["GOOSE", "COW", "SHEEP"]
ALL_CROPS = ["WHEAT", "CARROT", "STRAWBERRY", "TOMATO", "MELON"]

def extract_metrics(steps, seat):
    n_steps = len(steps)
    
    # 1. Day-by-day metrics (Day 0 to 29)
    # Day d end step: (d + 1) * 24 - 1
    daily_stats = []
    ndays = min(30, n_steps // 24)
    
    for d in range(ndays):
        step_idx = min(n_steps - 1, (d + 1) * 24 - 1)
        obs = steps[step_idx][seat]['observation']
        farm = obs['farms'][seat]
        
        cash = float(farm.get('money', 0.0))
        hands = len(farm.get('hands', []))
        
        # Count animals and crops
        animals = {a: 0 for a in ANIMAL_KEYS}
        crops = {c: 0 for c in ALL_CROPS}
        
        for row in farm.get('tiles', []):
            for tile in row:
                if isinstance(tile, dict):
                    an = tile.get('animal')
                    if an in animals:
                        animals[an] += 1
                    cr = tile.get('crop')
                    if cr in crops:
                        crops[cr] += 1
                    elif cr:
                        crops[cr] = crops.get(cr, 0) + 1
                        
        daily_stats.append({
            'day': d,
            'cash': cash,
            'hands': hands,
            'animals': animals,
            'crops': crops
        })
        
    # 2. Sales by period (d0-11, d12-18, d19-29)
    periods = {
        'd0-11': (0, 12 * 24),
        'd12-18': (12 * 24, 19 * 24),
        'd19-29': (19 * 24, n_steps)
    }
    period_sales = {p: {} for p in periods}
    
    for p_name, (start_step, end_step) in periods.items():
        for i in range(max(1, start_step), min(end_step, n_steps)):
            prev_obs = steps[i - 1][seat]['observation']
            cur_obs = steps[i][seat]['observation']
            action = steps[i][seat].get('action') or {}
            pre_shed = dict(prev_obs['private']['shed']) if prev_obs.get('private') else {}
            prev_inventories = prev_obs['private']['inventories'] if prev_obs.get('private') else []
            prices = cur_obs['market']['prices'] if cur_obs.get('market') else {}

            deposits = {}
            withdrawals = {}
            commands = [action.get('farmer', ['PASS'])] + list(action.get('hands') or [])
            for actor, cmd in enumerate(commands):
                if not cmd:
                    continue
                if cmd[0] == 'DROP':
                    inv = prev_inventories[actor] if actor < len(prev_inventories) else {}
                    for item, qty in inv.items():
                        deposits[item] = deposits.get(item, 0) + qty
                elif cmd[0] == 'PLACE' and len(cmd) >= 3:
                    deposits[cmd[1]] = deposits.get(cmd[1], 0) + cmd[2]
                elif cmd[0] == 'PICKUP' and len(cmd) >= 2:
                    qty = cmd[2] if len(cmd) >= 3 else 1
                    withdrawals[cmd[1]] = withdrawals.get(cmd[1], 0) + qty

            running = dict(pre_shed)
            for item, qty in deposits.items():
                running[item] = running.get(item, 0) + qty
            for item, qty in withdrawals.items():
                running[item] = running.get(item, 0) - qty

            for order in action.get('market') or []:
                if not order:
                    continue
                op = order[0]
                if op == 'BUY_PRODUCT' and len(order) >= 3:
                    running[order[1]] = running.get(order[1], 0) + order[2]
                elif op == 'SELL' and len(order) >= 3:
                    item, qty = order[1], order[2]
                    avail = running.get(item, 0)
                    actual = max(0, min(qty, avail))
                    running[item] = avail - actual
                    if actual > 0:
                        if item not in period_sales[p_name]:
                            period_sales[p_name][item] = {'units': 0, 'weighted_price_sum': 0}
                        price = prices.get(item, 0)
                        period_sales[p_name][item]['units'] += actual
                        period_sales[p_name][item]['weighted_price_sum'] += actual * price

    # 3. Milestones
    # First two shops
    unlocked_shops = []
    for s_idx in range(n_steps):
        town = steps[s_idx][seat]['observation'].get('town', {})
        shops = town.get('unlocked_shops', [])
        if len(shops) >= 2:
            unlocked_shops = shops[:2]
            break
        elif shops and not unlocked_shops:
            unlocked_shops = list(shops)
            
    # First HIRE step
    first_hire_step = None
    first_pasture_step = None
    
    for s_idx in range(n_steps):
        act = steps[s_idx][seat].get('action') or {}
        # Market orders for HIRE
        for order in act.get('market', []):
            if order and order[0] == 'HIRE' and first_hire_step is None:
                first_hire_step = s_idx
        # Hand / farmer actions for BUILD_PASTURE
        f_act = act.get('farmer', [])
        if f_act and (f_act == 'BUILD_PASTURE' or f_act[0] == 'BUILD_PASTURE') and first_pasture_step is None:
            first_pasture_step = s_idx
        for h_act in act.get('hands', []):
            if h_act and (h_act == 'BUILD_PASTURE' or h_act[0] == 'BUILD_PASTURE') and first_pasture_step is None:
                first_pasture_step = s_idx

    final_cash = float(steps[-1][seat]['observation']['farms'][seat].get('money', 0.0))

    return {
        'daily_stats': daily_stats,
        'period_sales': period_sales,
        'first_two_shops': unlocked_shops,
        'first_hire_step': first_hire_step,
        'first_pasture_step': first_pasture_step,
        'final_cash': final_cash
    }

def run_exp017_local():
    print("Running local EXP-017 matches (seeds 2140-2149, both seats)...")
    results = []
    seeds = list(range(2140, 2150))
    for s in seeds:
        # Seat 0: Candidate vs Parent
        print(f"  Seed {s} Seat 0...")
        env0 = make("kaggriculture", configuration={"seed": s, "episodeSteps": 720})
        env0.run([CANDIDATE_PATH, PARENT_PATH])
        m0 = extract_metrics(env0.steps, 0)
        m0['seed'] = s
        m0['seat'] = 0
        m0['result'] = "WIN" if env0.steps[-1][0]['reward'] > env0.steps[-1][1]['reward'] else ("LOSS" if env0.steps[-1][0]['reward'] < env0.steps[-1][1]['reward'] else "TIE")
        results.append(m0)
        
        # Seat 1: Parent vs Candidate
        print(f"  Seed {s} Seat 1...")
        env1 = make("kaggriculture", configuration={"seed": s, "episodeSteps": 720})
        env1.run([PARENT_PATH, CANDIDATE_PATH])
        m1 = extract_metrics(env1.steps, 1)
        m1['seed'] = s
        m1['seat'] = 1
        m1['result'] = "WIN" if env1.steps[-1][1]['reward'] > env1.steps[-1][0]['reward'] else ("LOSS" if env1.steps[-1][1]['reward'] < env1.steps[-1][0]['reward'] else "TIE")
        results.append(m1)
        
    return results

def main():
    if not EPISODES_JSON.exists():
        print(f"Error: {EPISODES_JSON} does not exist.")
        sys.exit(1)
        
    with open(EPISODES_JSON, 'r', encoding='utf-8') as f:
        episodes_meta = json.load(f)
        
    print(f"Processing {len(episodes_meta)} downloaded replays...")
    team_metrics = {}
    
    for ep in episodes_meta:
        t_name = ep['team_name']
        if t_name not in team_metrics:
            team_metrics[t_name] = []
            
        p = Path(ep['replay_path'])
        if not p.exists():
            print(f"Warning: {p} missing")
            continue
            
        with open(p, 'r', encoding='utf-8') as f:
            rep = json.load(f)
            
        seat = ep['seat']
        metrics = extract_metrics(rep['steps'], seat)
        metrics['episode_id'] = ep['episode_id']
        metrics['seed'] = ep['seed']
        metrics['seat'] = ep['seat']
        metrics['result'] = ep['result']
        metrics['opponent'] = ep['opponent']
        team_metrics[t_name].append(metrics)
        
    # Local EXP-017 matches
    exp017_metrics = run_exp017_local()
    team_metrics['EXP-017 (Local)'] = exp017_metrics
    
    # Save all raw metrics
    with open(OUTPUT_STATS_JSON, 'w', encoding='utf-8') as f:
        json.dump(team_metrics, f, indent=2, ensure_ascii=False)
        
    print(f"Saved aggregated metrics to {OUTPUT_STATS_JSON}")

if __name__ == '__main__':
    main()
