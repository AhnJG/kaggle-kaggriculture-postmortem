import json
from pathlib import Path
import statistics

STATS_JSON = Path("analysis/top_agents_20260923/stats_summary.json")
REPORT_MD = Path("coordination/reports/antigravity/20260923-2000-TOP-AGENT-SNAPSHOT.md")

def mean_or_zero(vals):
    return statistics.mean(vals) if vals else 0.0

def median_or_zero(vals):
    return statistics.median(vals) if vals else 0.0

def generate_report():
    with open(STATS_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    teams = list(data.keys())
    
    # We want:
    # 1. Summary Overview Table (Team, N matches, W/D/L, WinRate, Mean Cash Final, Mean First Hire Step, Mean First Pasture Step, Most Common 2 Shops)
    # 2. Milestones Table (First Two Shops, First HIRE step, First BUILD_PASTURE step, Final Cash)
    # 3. Day-by-Day Trajectory Table (Cash, Hands, Animals, Crop Tiles by kind at days 0, 3, 6, 9, 12, 15, 18, 21, 24, 27, 29)
    # 4. Sales by Period Table (d0-11, d12-18, d19-29): Units sold & Avg Price per item
    
    lines = []
    
    # Header per AGENTS.md §10.1
    # Notice: Pure Hangul and English only, NO Hanja characters!
    lines.append("VERDICT | 상위 3팀(DSM, Majkel1337, M & M & P & Q) 공개 리플레이 120개 및 EXP-017 로컬 20경기 관찰 집계 완료 | analysis/top_agents_20260923/episodes.json | 40경기/팀 + EXP-017 대조군 지표 추출 | NEXT ACTION: Claude 및 codex-astra가 차이점 분석 및 전략 수립에 활용")
    lines.append("")
    lines.append("1. **무엇을 바꾸거나 시험하는가**")
    lines.append("   - Leaderboard 상위 3팀(DSM, Majkel1337, M & M & P & Q)의 공개 완료 경기 리플레이 총 120개를 다운로드하여 자원 운용 지표를 집계하고, 우리 최신 후보인 EXP-017(로컬 seed 2140-2149, 양 좌석 총 20경기)과 나란히 비교합니다.")
    lines.append("2. **왜 하는가**")
    lines.append("   - 1위(DSM 3157.3) 등 최상위 봇들이 우리 에이전트와 어떤 시점(일꾼 고용, 목초지 건설, 동물 구성, 작물 구성, 매도 시기 및 품목)에서 갈라지는지 객관적인 관찰 자료를 확보하기 위함입니다. (해석 및 전략 제안은 배제)")
    lines.append("3. **무엇을 측정했고 결과가 어땠는가**")
    lines.append("   - 팀별 40개 최신 경기 및 EXP-017 로컬 20경기에 대해 일자별 현금(cash), 일꾼 수(hands), 동물 수(COW/SHEEP/GOOSE), 작물 타일 수, 품목별 판매 단위 및 단가(d0-11, d12-18, d19-29), 주요 마일스톤(첫 2개 상점, 첫 고용 step, 첫 목초지 건설 step, 최종 현금)을 전수 집계했습니다.")
    lines.append("4. **무엇이 막혀 있고 다음 행동은 무엇인가**")
    lines.append("   - 막힌 점: 없음 (Replay 120개 다운로드 및 추출 완료)")
    lines.append("   - 다음 행동 1: Claude가 상위 팀과 EXP-017 간의 수치 격차 및 분기 시점을 분석")
    lines.append("   - 다음 행동 2: Codex-astra가 분석 결과를 바탕으로 신규 전략 가설 카드 수립")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 1. 개요 및 주요 마일스톤 비교 (Milestones)")
    lines.append("")
    lines.append("| 에이전트 / 팀 | 경기 수 | 승/무/패 (승률) | 평균 최종 현금 | 중앙값 최종 현금 | 첫 HIRE step (평균) | 첫 BUILD_PASTURE step (평균) | 첫 2개 상점 주요 조합 |")
    lines.append("|---|---|---|---|---|---|---|---|")
    
    for team in teams:
        matches = data[team]
        n = len(matches)
        wins = sum(1 for m in matches if m['result'] == 'WIN')
        ties = sum(1 for m in matches if m['result'] == 'TIE')
        losses = sum(1 for m in matches if m['result'] == 'LOSS')
        win_rate = (wins + 0.5 * ties) / n * 100 if n > 0 else 0.0
        
        final_cashes = [m['final_cash'] for m in matches]
        mean_cash = mean_or_zero(final_cashes)
        med_cash = median_or_zero(final_cashes)
        
        hire_steps = [m['first_hire_step'] for m in matches if m['first_hire_step'] is not None]
        mean_hire = f"{mean_or_zero(hire_steps):.1f}" if hire_steps else "None"
        
        pasture_steps = [m['first_pasture_step'] for m in matches if m['first_pasture_step'] is not None]
        mean_pasture = f"{mean_or_zero(pasture_steps):.1f}" if pasture_steps else "None"
        
        # Shop combinations
        shop_combos = {}
        for m in matches:
            s_pair = " + ".join(m.get('first_two_shops', [])) if m.get('first_two_shops') else "None"
            shop_combos[s_pair] = shop_combos.get(s_pair, 0) + 1
        sorted_shops = sorted(shop_combos.items(), key=lambda x: x[1], reverse=True)
        top_shop_str = f"{sorted_shops[0][0]} ({sorted_shops[0][1]}/{n})" if sorted_shops else "N/A"
        
        lines.append(f"| **{team}** | {n} | {wins}/{ties}/{losses} ({win_rate:.1f}%) | {mean_cash:,.0f} | {med_cash:,.0f} | {mean_hire} | {mean_pasture} | {top_shop_str} |")
        
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 2. 일자별 현금(Cash) 및 일꾼 수(Hands) 추이")
    lines.append("")
    sample_days = [0, 2, 5, 8, 11, 14, 17, 20, 23, 26, 29]
    lines.append("| 팀 | 지표 | Day 0 | Day 2 | Day 5 | Day 8 | Day 11 | Day 14 | Day 17 | Day 20 | Day 23 | Day 26 | Day 29 |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    
    for team in teams:
        matches = data[team]
        cash_by_day = {d: [] for d in sample_days}
        hands_by_day = {d: [] for d in sample_days}
        for m in matches:
            for d_stat in m['daily_stats']:
                d = d_stat['day']
                if d in sample_days:
                    cash_by_day[d].append(d_stat['cash'])
                    hands_by_day[d].append(d_stat['hands'])
                    
        cash_str = " | ".join(f"{mean_or_zero(cash_by_day[d]):,.0f}" for d in sample_days)
        hands_str = " | ".join(f"{mean_or_zero(hands_by_day[d]):.1f}" for d in sample_days)
        lines.append(f"| **{team}** | 평균 Cash | {cash_str} |")
        lines.append(f"| | 평균 Hands | {hands_str} |")
        
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 3. 일자별 보유 동물 수 (COW / SHEEP / GOOSE) 추이")
    lines.append("")
    lines.append("| 팀 | 동물 종류 | Day 0 | Day 2 | Day 5 | Day 8 | Day 11 | Day 14 | Day 17 | Day 20 | Day 23 | Day 26 | Day 29 |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    
    for team in teams:
        matches = data[team]
        cow_by_day = {d: [] for d in sample_days}
        sheep_by_day = {d: [] for d in sample_days}
        goose_by_day = {d: [] for d in sample_days}
        for m in matches:
            for d_stat in m['daily_stats']:
                d = d_stat['day']
                if d in sample_days:
                    cow_by_day[d].append(d_stat['animals'].get('COW', 0))
                    sheep_by_day[d].append(d_stat['animals'].get('SHEEP', 0))
                    goose_by_day[d].append(d_stat['animals'].get('GOOSE', 0))
                    
        c_str = " | ".join(f"{mean_or_zero(cow_by_day[d]):.1f}" for d in sample_days)
        s_str = " | ".join(f"{mean_or_zero(sheep_by_day[d]):.1f}" for d in sample_days)
        g_str = " | ".join(f"{mean_or_zero(goose_by_day[d]):.1f}" for d in sample_days)
        lines.append(f"| **{team}** | COW | {c_str} |")
        lines.append(f"| | SHEEP | {s_str} |")
        lines.append(f"| | GOOSE | {g_str} |")
        
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 4. 일자별 작물 타일 수 (Crop Tiles) 추이")
    lines.append("")
    crops_to_show = ["WHEAT", "CARROT", "STRAWBERRY", "TOMATO", "MELON"]
    lines.append("| 팀 | 작물 | Day 0 | Day 2 | Day 5 | Day 8 | Day 11 | Day 14 | Day 17 | Day 20 | Day 23 | Day 26 | Day 29 |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    
    for team in teams:
        matches = data[team]
        crop_stats = {c: {d: [] for d in sample_days} for c in crops_to_show}
        for m in matches:
            for d_stat in m['daily_stats']:
                d = d_stat['day']
                if d in sample_days:
                    for c in crops_to_show:
                        crop_stats[c][d].append(d_stat['crops'].get(c, 0))
                        
        for c_idx, c in enumerate(crops_to_show):
            row_prefix = f"| **{team}**" if c_idx == 0 else "| "
            c_str = " | ".join(f"{mean_or_zero(crop_stats[c][d]):.1f}" for d in sample_days)
            lines.append(f"{row_prefix} | {c} | {c_str} |")
            
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 5. 기간별 품목 매도량 및 가중평균 가격 (Sales Units & Price)")
    lines.append("")
    periods = ['d0-11', 'd12-18', 'd19-29']
    
    for p in periods:
        lines.append(f"### 기간: {p}")
        lines.append("")
        lines.append("| 품목 (Item) | " + " | ".join(f"**{t}** (단위/단가)" for t in teams) + " |")
        lines.append("|---| " + " | ".join("---" for _ in teams) + " |")
        
        # Collect all items sold in this period across all teams
        all_items = set()
        for t in teams:
            for m in data[t]:
                all_items.update(m['period_sales'].get(p, {}).keys())
        all_items = sorted(list(all_items))
        
        for item in all_items:
            cells = []
            for t in teams:
                matches = data[t]
                n = len(matches)
                total_units = 0
                total_val = 0
                for m in matches:
                    s_data = m['period_sales'].get(p, {}).get(item, {'units': 0, 'weighted_price_sum': 0})
                    total_units += s_data['units']
                    total_val += s_data['weighted_price_sum']
                avg_units_per_game = total_units / n if n > 0 else 0
                avg_price = total_val / total_units if total_units > 0 else 0
                cells.append(f"{avg_units_per_game:.1f}u @ {avg_price:.1f}")
            lines.append(f"| **{item}** | " + " | ".join(cells) + " |")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## 6. 관찰 원본 데이터 위치")
    lines.append("- 에피소드 메타데이터: `analysis/top_agents_20260923/episodes.json`")
    lines.append("- 전수 집계 원본 통계: `analysis/top_agents_20260923/stats_summary.json`")
    lines.append("- 다운로드 리플레이 원본: `private_artifacts/top_agents_20260923/raw/*.json` (총 120개)")
    lines.append("")
    
    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_MD, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines) + "\n")
        
    print(f"Report written to {REPORT_MD}")

if __name__ == '__main__':
    generate_report()
