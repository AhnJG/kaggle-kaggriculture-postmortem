import json
import statistics
import math
import numpy as np
from scipy.stats import spearmanr
from collections import defaultdict

def sign(x):
    return 1 if x > 0 else -1 if x < 0 else 0

def load_data():
    games = []
    with open('experiments/p4b_20260926/games.jsonl', 'r') as f:
        for line in f:
            if not line.strip(): continue
            games.append(json.loads(line))
    
    with open('experiments/p4b_20260926/episodes.json', 'r') as f:
        episodes = json.load(f)
    ep_map = {ep['id']: ep for ep in episodes}
    for g in games:
        if g['episode'] in ep_map:
            g['opp_path'] = ep_map[g['episode']]['opp_path']
    return games

CANDIDATES = ['v171', 'v173', 'v111', 'v074', 'c171_173']

def calc_metrics(games, source_filter=None):
    if source_filter:
        games = [g for g in games if source_filter(g['source'])]
        
    data = {}
    for g in games:
        eid = g['episode']
        mode = g['mode']
        cand = g['candidate_name']
        if eid not in data:
            data[eid] = {'open': {}, 'closed': {}, 'opp_path': g.get('opp_path', '')}
        data[eid][mode][cand] = {
            'margin': g['margin'], 
            'score': g['score'],
            'rewards': g['rewards']
        }

    deltas = []
    closed_stats = []
    
    for eid, modes in data.items():
        if 'P' not in modes['open'] or 'P' not in modes['closed']:
            continue
        for cand in CANDIDATES:
            if cand not in modes['open'] or cand not in modes['closed']:
                continue
            delta_open = modes['open'][cand]['margin'] - modes['open']['P']['margin']
            delta_closed = modes['closed'][cand]['margin'] - modes['closed']['P']['margin']
            delta_score_open = modes['open'][cand]['score'] - modes['open']['P']['score']
            delta_score_closed = modes['closed'][cand]['score'] - modes['closed']['P']['score']
            
            deltas.append({
                'episode': eid,
                'candidate': cand,
                'delta_open': delta_open,
                'delta_closed': delta_closed,
                'delta_score_open': delta_score_open,
                'delta_score_closed': delta_score_closed,
                'informative': abs(delta_open) >= 1 or abs(delta_closed) >= 1,
                'informative_score': abs(delta_score_open) > 0 or abs(delta_score_closed) > 0
            })
            
            c_score = modes['closed'][cand]['score']
            
            closed_stats.append({
                'episode': eid,
                'candidate': cand,
                'opp_path': modes['opp_path'],
                'delta_margin_closed': delta_closed,
                'delta_score_closed': delta_score_closed,
                'score': c_score
            })
            
    informative = [d for d in deltas if d['informative']]
    D = sum(1 for d in informative if sign(d['delta_open']) == sign(d['delta_closed'])) / len(informative) if informative else 0
    
    inf_score = [d for d in deltas if d['informative_score']]
    D_score = sum(1 for d in inf_score if sign(d['delta_score_open']) == sign(d['delta_score_closed'])) / len(inf_score) if inf_score else 0

    avg_open = []
    avg_closed = []
    for cand in CANDIDATES:
        cand_deltas = [d for d in deltas if d['candidate'] == cand]
        if not cand_deltas: continue
        avg_open.append(statistics.mean(d['delta_open'] for d in cand_deltas))
        avg_closed.append(statistics.mean(d['delta_closed'] for d in cand_deltas))
    
    rho = spearmanr(avg_open, avg_closed)[0] if len(avg_open) > 1 else 0
    if math.isnan(rho): rho = 0

    if informative:
        M = np.median([abs(d['delta_open']) for d in informative]) / max(np.median([abs(d['delta_closed']) for d in informative]), 1e-9)
    else:
        M = 0

    return {
        'deltas': deltas,
        'informative': informative,
        'D': D,
        'D_score': D_score,
        'rho': float(rho),
        'M': float(M),
        'avg_open': avg_open,
        'avg_closed': avg_closed,
        'closed_stats': closed_stats
    }

def bootstrap_CI(deltas, n_boot=2000):
    np.random.seed(42)
    episodes = list(set(d['episode'] for d in deltas))
    n_ep = len(episodes)
    if n_ep == 0:
        return {'D_025': 0, 'D_975': 0, 'rho_025': 0, 'rho_975': 0}
        
    Ds = []
    rhos = []
    
    ep_to_deltas = defaultdict(list)
    for d in deltas:
        ep_to_deltas[d['episode']].append(d)
        
    for _ in range(n_boot):
        resampled_eps = np.random.choice(episodes, n_ep, replace=True)
        boot_deltas = []
        for ep in resampled_eps:
            boot_deltas.extend(ep_to_deltas[ep])
            
        inf = [d for d in boot_deltas if d['informative']]
        if inf:
            Ds.append(sum(1 for d in inf if sign(d['delta_open']) == sign(d['delta_closed'])) / len(inf))
        
        avg_open = []
        avg_closed = []
        for cand in CANDIDATES:
            cand_deltas = [d for d in boot_deltas if d['candidate'] == cand]
            if cand_deltas:
                avg_open.append(statistics.mean(d['delta_open'] for d in cand_deltas))
                avg_closed.append(statistics.mean(d['delta_closed'] for d in cand_deltas))
        r = spearmanr(avg_open, avg_closed)[0] if len(avg_open) > 1 else 0
        if math.isnan(r): r = 0
        rhos.append(r)
        
    return {
        'D_025': float(np.percentile(Ds, 2.5)) if Ds else 0,
        'D_975': float(np.percentile(Ds, 97.5)) if Ds else 0,
        'rho_025': float(np.percentile(rhos, 2.5)) if rhos else 0,
        'rho_975': float(np.percentile(rhos, 97.5)) if rhos else 0,
    }

def bootstrap_closed_CI(closed_stats, n_boot=2000):
    np.random.seed(42)
    episodes = list(set(d['episode'] for d in closed_stats))
    n_ep = len(episodes)
    if n_ep == 0:
        return {}
        
    ep_to_stats = defaultdict(list)
    for s in closed_stats:
        ep_to_stats[s['episode']].append(s)
        
    res_margins = defaultdict(list)
    res_scores = defaultdict(list)
    
    for _ in range(n_boot):
        resampled_eps = np.random.choice(episodes, n_ep, replace=True)
        boot_stats = []
        for ep in resampled_eps:
            boot_stats.extend(ep_to_stats[ep])
            
        for cand in CANDIDATES:
            c_stats = [s for s in boot_stats if s['candidate'] == cand]
            if c_stats:
                res_margins[cand].append(statistics.mean(s['delta_margin_closed'] for s in c_stats))
                res_scores[cand].append(statistics.mean(s['delta_score_closed'] for s in c_stats))
                
    out = {}
    for cand in CANDIDATES:
        if cand in res_margins:
            out[cand] = {
                'margin_025': float(np.percentile(res_margins[cand], 2.5)),
                'margin_975': float(np.percentile(res_margins[cand], 97.5)),
                'score_025': float(np.percentile(res_scores[cand], 2.5)),
                'score_975': float(np.percentile(res_scores[cand], 97.5)),
            }
    return out
    
def main():
    games = load_data()
    all_metrics = calc_metrics(games)
    ci_all = bootstrap_CI(all_metrics['deltas'])
    
    a_metrics = calc_metrics(games, lambda s: s == 'A')
    ci_a = bootstrap_CI(a_metrics['deltas'])

    var_stats = {}
    for cand in CANDIDATES:
        c_deltas = [d for d in all_metrics['deltas'] if d['candidate'] == cand]
        c_inf = [d for d in c_deltas if d['informative']]
        cD = sum(1 for d in c_inf if sign(d['delta_open']) == sign(d['delta_closed'])) / len(c_inf) if c_inf else 0
        cAvgOpen = statistics.mean(d['delta_open'] for d in c_deltas) if c_deltas else 0
        cAvgClosed = statistics.mean(d['delta_closed'] for d in c_deltas) if c_deltas else 0
        var_stats[cand] = {
            'informative_n': len(c_inf),
            'D': cD,
            'avg_delta_open': cAvgOpen,
            'avg_delta_closed': cAvgClosed
        }

    closed_ci = bootstrap_closed_CI(all_metrics['closed_stats'])
    cand_closed_summary = {}
    for cand in CANDIDATES:
        c_stats = [s for s in all_metrics['closed_stats'] if s['candidate'] == cand]
        if not c_stats: continue
        
        avg_margin = statistics.mean(s['delta_margin_closed'] for s in c_stats)
        avg_score = statistics.mean(s['delta_score_closed'] for s in c_stats)
        
        opp_stats = defaultdict(lambda: {'W': 0, 'D': 0, 'L': 0})
        for s in c_stats:
            opp_name = s['opp_path'].split('/')[-1]
            if s['score'] > 0:
                opp_stats[opp_name]['W'] += 1
            elif s['score'] < 0:
                opp_stats[opp_name]['L'] += 1
            else:
                opp_stats[opp_name]['D'] += 1
                
        cand_closed_summary[cand] = {
            'avg_delta_margin': avg_margin,
            'avg_delta_score': avg_score,
            'CI': closed_ci.get(cand, {}),
            'opponents': dict(opp_stats)
        }

    summary = {
        'all': {
            'D': all_metrics['D'],
            'D_score': all_metrics['D_score'],
            'rho': all_metrics['rho'],
            'M': all_metrics['M'],
            'informative_n': len(all_metrics['informative']),
            'CI': ci_all
        },
        'source_A': {
            'D': a_metrics['D'],
            'D_score': a_metrics['D_score'],
            'rho': a_metrics['rho'],
            'M': a_metrics['M'],
            'informative_n': len(a_metrics['informative']),
            'CI': ci_a
        },
        'variants': var_stats,
        'candidates_closed': cand_closed_summary
    }

    with open('experiments/p4b_20260926/summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
        
    print("Written summary.json")

if __name__ == '__main__':
    main()
