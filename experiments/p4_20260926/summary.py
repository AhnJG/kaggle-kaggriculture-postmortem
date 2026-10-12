import json
import statistics
import math
import sys
from scipy.stats import spearmanr
import numpy as np
import time

def sign(x):
    return 1 if x > 0 else -1 if x < 0 else 0

def load_data():
    games = []
    with open('experiments/p4_20260926/games.jsonl', 'r') as f:
        for line in f:
            if not line.strip(): continue
            games.append(json.loads(line))
    return games

def calc_metrics(games, source_filter=None):
    if source_filter:
        games = [g for g in games if source_filter(g['source'])]
    
    # Organize by (episode, mode) -> candidate -> margin/score
    data = {}
    for g in games:
        eid = g['episode']
        mode = g['mode']
        cand = g['candidate_name']
        if eid not in data:
            data[eid] = {'open': {}, 'closed': {}}
        data[eid][mode][cand] = {'margin': g['margin'], 'score': g['score']}

    # Compute deltas
    deltas = []
    for eid, modes in data.items():
        if 'P' not in modes['open'] or 'P' not in modes['closed']:
            continue
        for cand in ['v000', 'v002', 'v004', 'v006', 'v008', 'v010']:
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
            
    informative = [d for d in deltas if d['informative']]
    D = sum(1 for d in informative if sign(d['delta_open']) == sign(d['delta_closed'])) / len(informative) if informative else 0
    
    inf_score = [d for d in deltas if d['informative_score']]
    D_score = sum(1 for d in inf_score if sign(d['delta_score_open']) == sign(d['delta_score_closed'])) / len(inf_score) if inf_score else 0

    # rho
    avg_open = []
    avg_closed = []
    for cand in ['v000', 'v002', 'v004', 'v006', 'v008', 'v010']:
        cand_deltas = [d for d in deltas if d['candidate'] == cand]
        if not cand_deltas: continue
        avg_open.append(statistics.mean(d['delta_open'] for d in cand_deltas))
        avg_closed.append(statistics.mean(d['delta_closed'] for d in cand_deltas))
    
    rho = spearmanr(avg_open, avg_closed)[0] if len(avg_open) > 1 else 0
    if math.isnan(rho): rho = 0

    # M
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
        'avg_closed': avg_closed
    }

def bootstrap_CI(deltas, n_boot=2000):
    np.random.seed(42)
    # Group by episode to resample episodes
    episodes = list(set(d['episode'] for d in deltas))
    n_ep = len(episodes)
    
    Ds = []
    rhos = []
    
    for _ in range(n_boot):
        # resample episodes
        resampled_eps = np.random.choice(episodes, n_ep, replace=True)
        # build resampled deltas
        # to handle duplicates properly, just extract deltas for each chosen episode
        # pre-index deltas by episode
        ep_to_deltas = {}
        for d in deltas:
            ep_to_deltas.setdefault(d['episode'], []).append(d)
            
        boot_deltas = []
        for ep in resampled_eps:
            boot_deltas.extend(ep_to_deltas[ep])
            
        inf = [d for d in boot_deltas if d['informative']]
        if inf:
            Ds.append(sum(1 for d in inf if sign(d['delta_open']) == sign(d['delta_closed'])) / len(inf))
        
        # rho
        avg_open = []
        avg_closed = []
        for cand in ['v000', 'v002', 'v004', 'v006', 'v008', 'v010']:
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

def main():
    games = load_data()
    all_metrics = calc_metrics(games)
    ci_all = bootstrap_CI(all_metrics['deltas'])
    
    a_metrics = calc_metrics(games, lambda s: s == 'A')
    ci_a = bootstrap_CI(a_metrics['deltas'])

    # Variant-specific D
    var_stats = {}
    for cand in ['v000', 'v002', 'v004', 'v006', 'v008', 'v010']:
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
        'variants': var_stats
    }

    with open('experiments/p4_20260926/summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
        
    print("Written summary.json")

if __name__ == '__main__':
    main()
