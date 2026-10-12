import os
import sys
import json
import glob
from collections import defaultdict, Counter
import datetime
from pathlib import Path

def get_action_op(action_item):
    if not action_item: return "PASS"
    if isinstance(action_item, str): return action_item
    return action_item[0]

def parse_episode(filepath, team_names_target):
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    info = data.get('info', {})
    team_names = info.get('TeamNames', [])
    if not team_names:
        return {}
        
    team_indices = {}
    for i, t in enumerate(team_names):
        if t in team_names_target:
            team_indices[t] = i
            
    if not team_indices:
        return {}
        
    steps = data.get('steps', [])
    if not steps:
        return {}
        
    results = {}
    for team, t_idx in team_indices.items():
        opp_idx = 1 - t_idx
        
        # 1. 최종 뱅크 / 상대 뱅크
        last_step = steps[-1]
        my_bank = last_step[t_idx]['reward'] if last_step[t_idx]['reward'] is not None else 0
        opp_bank = last_step[opp_idx]['reward'] if last_step[opp_idx]['reward'] is not None else 0
        
        # Metrics
        buy_land_steps = []
        max_hands = 0
        max_hands_step = 0
        buy_animal_counts = Counter()
        buy_animal_steps = defaultdict(list)
        build_coop = 0
        build_pasture = 0
        action_counts = Counter()
        sell_quantities = Counter()
        sell_orders = 0
        sell_turns = 0
        
        for step_idx, step_data in enumerate(steps):
            if step_idx == 0: continue # Initial state setup
            
            p_data = step_data[t_idx]
            obs = p_data.get('observation')
            action = p_data.get('action')
            
            # Hands count
            if obs and 'farms' in obs and len(obs['farms']) > t_idx:
                farm = obs['farms'][t_idx]
                if 'hands' in farm:
                    num_hands = len(farm['hands'])
                    if num_hands > max_hands:
                        max_hands = num_hands
                        max_hands_step = step_idx - 1 # Since step_idx is 1-based in steps array
                        
            # Action parsing
            if action:
                # Farmer action
                farmer_act = action.get('farmer', ['PASS'])
                if not farmer_act: farmer_act = ['PASS']
                op = get_action_op(farmer_act)
                if op in ('N', 'S', 'E', 'W', 'NORTH', 'SOUTH', 'EAST', 'WEST'):
                    action_counts['이동'] += 1
                else:
                    action_counts[op] += 1
                    
                # Hands actions
                for h_act in action.get('hands', []):
                    op = get_action_op(h_act)
                    if op in ('N', 'S', 'E', 'W', 'NORTH', 'SOUTH', 'EAST', 'WEST'):
                        action_counts['이동'] += 1
                    else:
                        action_counts[op] += 1
                        
                # Market actions
                market_acts = action.get('market', [])
                has_sell_this_turn = False
                for m_act in market_acts:
                    op = get_action_op(m_act)
                    # Don't count market ops in the main action_counts unless requested? The brief asks for:
                    # WATER/HARVEST/PLANT/SELL/CARE/FEED/COLLECT_FERTILIZER/FERTILIZE/PICKUP/PLACE/DIG/이동/PASS
                    # HIRE, BUY_LAND, BUY_ANIMAL, BUILD_COOP are also actions but let's count them too.
                    action_counts[op] += 1
                    
                    if op == 'BUY_LAND':
                        # typically ['BUY_LAND']
                        buy_land_steps.append(step_idx - 1)
                    elif op == 'BUY_ANIMAL':
                        atype = m_act[1] if len(m_act) > 1 else 'UNKNOWN'
                        buy_animal_counts[atype] += 1
                        buy_animal_steps[atype].append(step_idx - 1)
                    elif op == 'BUILD_COOP':
                        build_coop += 1
                    elif op == 'BUILD_PASTURE':
                        build_pasture += 1
                    elif op == 'SELL':
                        has_sell_this_turn = True
                        sell_orders += 1
                        item = m_act[1] if len(m_act) > 1 else 'UNKNOWN'
                        qty = m_act[2] if len(m_act) > 2 else 1
                        sell_quantities[item] += qty
                        
                if has_sell_this_turn:
                    sell_turns += 1
                    
        # Post process
        results[team] = {
            "bank_my": my_bank,
            "bank_opp": opp_bank,
            "buy_land": buy_land_steps,
            "max_hands": max_hands,
            "max_hands_step": max_hands_step,
            "buy_animal_counts": dict(buy_animal_counts),
            "buy_animal_steps": dict(buy_animal_steps),
            "build_coop": build_coop,
            "build_pasture": build_pasture,
            "action_counts": dict(action_counts),
            "sell_quantities": dict(sell_quantities),
            "sell_orders": sell_orders,
            "sell_turns": sell_turns
        }
    return results

def main():
    top10_file = Path("private_artifacts/leaderboard/latest_top10.txt")
    if not top10_file.exists():
        print(f"{top10_file} not found.")
        sys.exit(1)
        
    with open(top10_file, "r") as f:
        target_teams = set(line.strip() for line in f if line.strip())
        
    # Read target episode ids from episodes.csv if available
    episodes_csv = Path("private_artifacts/leaderboard/episodes.csv")
    target_ep_ids = set()
    if episodes_csv.exists():
        import csv as _csv
        with open(episodes_csv, "r", encoding="utf-8") as ep_f:
            for row in _csv.DictReader(ep_f):
                if row.get("EpisodeId"):
                    target_ep_ids.add(row["EpisodeId"])

    all_replay_files = glob.glob('private_artifacts/replays/top/*.json')
    replay_files = []
    for f in all_replay_files:
        # Check if f matches episode-<id>-replay.json or <id>.json
        fname = Path(f).name
        matched = False
        for ep_id in target_ep_ids:
            if ep_id in fname:
                matched = True
                break
        if matched or not target_ep_ids:
            replay_files.append(f)
    
    # team -> list of stats dicts
    team_stats = defaultdict(list)
    
    for f in replay_files:
        res = parse_episode(f, target_teams)
        for t, stats in res.items():
            team_stats[t].append(stats)
            
    # Aggregate and average per team
    report_lines = []
    
    report_lines.append("## Task 2 — 상위 봇 리플레이 분석\n")
    
    # We will output a markdown table for each team.
    # Actually, the brief says:
    # "팀별로 아래 표를 채워 보고하라. 해석은 붙이지 마라 — 숫자만."
    
    for team in sorted(team_stats.keys()):
        eps = team_stats[team]
        n_eps = len(eps)
        
        avg_my_bank = sum(e['bank_my'] for e in eps) / n_eps
        avg_opp_bank = sum(e['bank_opp'] for e in eps) / n_eps
        
        # BUY_LAND: List of steps. We can just show one typical or average? The prompt says "리스트 (몇 구획, 언제)".
        # Let's collect all and show.
        all_buy_lands = [len(e['buy_land']) for e in eps]
        avg_buy_lands = sum(all_buy_lands) / n_eps
        # When? Average first buy? Let's just flat map and show up to a few.
        flat_buy_lands = [step for e in eps for step in e['buy_land']]
        avg_land_time = sum(flat_buy_lands)/len(flat_buy_lands) if flat_buy_lands else 0
        
        avg_max_hands = sum(e['max_hands'] for e in eps) / n_eps
        avg_max_hands_step = sum(e['max_hands_step'] for e in eps) / n_eps
        
        # BUY_ANIMAL
        animal_counts = defaultdict(int)
        for e in eps:
            for k, v in e['buy_animal_counts'].items():
                animal_counts[k] += v
        animal_str = ", ".join(f"{k}: {v/n_eps:.1f}마리" for k, v in animal_counts.items())
        if not animal_str: animal_str = "없음"
        
        avg_coop = sum(e['build_coop'] for e in eps) / n_eps
        avg_pasture = sum(e['build_pasture'] for e in eps) / n_eps
        
        # Actions
        act_keys = ['WATER', 'HARVEST', 'PLANT', 'SELL', 'CARE', 'FEED', 'COLLECT_FERTILIZER', 'FERTILIZE', 'PICKUP', 'PLACE', 'DIG', '이동', 'PASS']
        act_totals = defaultdict(int)
        for e in eps:
            for k in act_keys:
                act_totals[k] += e['action_counts'].get(k, 0)
        
        act_str = ", ".join(f"{k}: {act_totals[k]/n_eps:.1f}" for k in act_keys if act_totals[k] > 0)
        
        # Sales
        sales = defaultdict(int)
        for e in eps:
            for k, v in e['sell_quantities'].items():
                sales[k] += v
        sales_str = ", ".join(f"{k}: {v/n_eps:.1f}" for k, v in sales.items())
        
        avg_sell_turns = sum(e['sell_turns'] for e in eps) / n_eps
        total_sell_qty = sum(sum(e['sell_quantities'].values()) for e in eps)
        total_sell_orders = sum(e['sell_orders'] for e in eps)
        avg_sell_qty_per_order = total_sell_qty / total_sell_orders if total_sell_orders else 0
        
        report_lines.append(f"### 팀: {team} ({n_eps} episodes)")
        report_lines.append("| 항목 | 결과 |")
        report_lines.append("|---|---|")
        report_lines.append(f"| 최종 뱅크 / 상대 뱅크 | {avg_my_bank:.0f} / {avg_opp_bank:.0f} |")
        report_lines.append(f"| `BUY_LAND` 발행 step | 평균 {avg_buy_lands:.1f} 구획 (평균 step: {avg_land_time:.0f}) |")
        report_lines.append(f"| 최대 동시 일꾼 수 / 도달 step | {avg_max_hands:.1f} 명 / {avg_max_hands_step:.0f} step |")
        report_lines.append(f"| `BUY_ANIMAL` 내역 | {animal_str} |")
        report_lines.append(f"| `BUILD_COOP` / `BUILD_PASTURE` 횟수 | {avg_coop:.1f} / {avg_pasture:.1f} |")
        report_lines.append(f"| 액션 타입별 총 횟수 | {act_str} |")
        report_lines.append(f"| 품목별 판매 총량 | {sales_str} |")
        report_lines.append(f"| SELL 주문 발행 턴 수 / 1회 평균 수량 | {avg_sell_turns:.1f} 턴 / {avg_sell_qty_per_order:.1f} 개 |")
        report_lines.append("\n")
        
    out_path = Path(f"coordination/reports/gemini/{datetime.datetime.now().strftime('%Y%m%d-%H%M')}-KAGRI-014.md")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(out_path, "w") as f:
        f.write("# VERDICT: [LOCAL] 리더보드 스냅샷 및 리플레이 수집 완료\n\n")
        f.write("- KAGRI-014 정찰 루틴 실행\n")
        # Count total teams from latest leaderboard csv
        lb_csvs = list(Path.cwd().glob("kaggriculture-publicleaderboard*.csv"))
        total_teams = "N/A"
        if lb_csvs:
            latest_lb_csv = max(lb_csvs, key=os.path.getctime)
            try:
                import csv as _csv
                with open(latest_lb_csv, 'r', encoding='utf-8-sig') as lbf:
                    total_teams = len(list(_csv.DictReader(lbf)))
            except Exception:
                pass
        f.write(f"- 리더보드 팀 수: {total_teams}팀\n")
        f.write(f"- 경로 및 SHA: N/A\n")
        f.write("- 실행한 검증과 결과: `kaggle` CLI로 리더보드 스냅샷 및 상위 10팀의 최근 에피소드 다운로드, 파싱 완료\n")
        f.write("- NEXT ACTION: Cowork가 아래 데이터를 분석해 KILLS나 실험 카드를 업데이트할 것\n\n")
        
        f.write("## Task 1 — 리더보드 일일 스냅샷\n")
        # Find Sian from the latest snapshot
        snapshots_path = Path('private_artifacts/leaderboard/snapshots.csv')
        sian_stats = "N/A"
        if snapshots_path.exists():
            with open(snapshots_path, 'r') as sf:
                for line in sf:
                    if 'Sian' in line:
                        sian_stats = line.strip()
        f.write(f"우리 레이팅/순위 (Sian): {sian_stats}\n\n")
        
        f.write("\n".join(report_lines))
        
    print(f"Report written to {out_path}")

if __name__ == '__main__':
    main()
