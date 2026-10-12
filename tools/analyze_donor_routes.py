#!/usr/bin/env python3
"""Descriptive donor analysis using strictly pre-action decision context."""
import argparse
from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path


def key(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'))


def composition(farm):
    counts = Counter()
    for row in farm['tiles']:
        for tile in row:
            if isinstance(tile, dict):
                counts[tile.get('crop') or tile.get('animal') or tile['kind']] += 1
    return dict(sorted(counts.items()))


def context(replay, seat, step):
    before = replay['steps'][step-1][seat]['observation']
    after = replay['steps'][step][seat]['observation']
    farm = before['farms'][seat]
    return {'pre_step': step-1, 'day': before['day'], 'hour': before['hour'],
            'seat': seat, 'cash': farm['money'], 'hands': len(farm['hands']),
            'farmer_position': farm['farmer'], 'hand_positions': farm['hands'],
            'shops': before['town']['unlocked_shops'],
            'prices': before['market']['prices'], 'market_inventory': before['market']['inventory'],
            'private': before['private'], 'composition': composition(farm),
            'opponent_cash': before['farms'][1-seat]['money'],
            'opponent_composition': composition(before['farms'][1-seat]),
            'opponent_previous_action_forensics_only': replay['steps'][step-1][1-seat]['action'],
            'action': replay['steps'][step][seat]['action'],
            'post_cash': after['farms'][seat]['money'],
            'post_hands': len(after['farms'][seat]['hands']), 'post_private': after['private']}


def analyze_group(entries):
    replays = [json.loads(Path(d['path']).read_text()) for d in entries]
    for d in entries:
        assert hashlib.sha256(Path(d['path']).read_bytes()).hexdigest() == d['sha256']
    actions = [[r['steps'][i][d['seat']]['action'] for i in range(1,720)] for d,r in zip(entries,replays)]
    metrics = {}
    for part in ['full', 'farmer', 'hands', 'market', 'field']:
        def project(a):
            return a if part == 'full' else [a['farmer'],a['hands']] if part == 'field' else a[part]
        different = [i+1 for i in range(719) if len({key(project(a[i])) for a in actions}) > 1]
        metrics[part] = {'all_three_equal': 719-len(different), 'total': 719,
                         'prefix_equal': different[0]-1 if different else 719,
                         'different_steps': different}
    nonempty = [i for i in range(719) if any(a[i]['market'] for a in actions)]
    metrics['market_nonempty_union'] = {'steps': len(nonempty),
        'all_three_equal': sum(len({key(a[i]['market']) for a in actions}) == 1 for i in nonempty)}
    cases = {}
    selected = {1,20,25,26,27,73,145,150,169,217,220}
    for day in range(30):
        day_diffs = [i for i in metrics['full']['different_steps'] if replays[0]['steps'][i-1][entries[0]['seat']]['observation']['day'] == day]
        if day_diffs:
            selected.add(day_diffs[0])
    for i in sorted(selected):
        cases[str(i)] = [dict(episode_id=d['episode']['id'], **context(r,d['seat'],i)) for d,r in zip(entries,replays)]
    pairs = []
    for a,b in itertools.combinations(range(len(entries)),2):
        dif = [i+1 for i in range(719) if actions[a][i] != actions[b][i]]
        pairs.append({'episodes':[entries[a]['episode']['id'], entries[b]['episode']['id']],
                      'same_seat': entries[a]['seat']==entries[b]['seat'],
                      'equal_steps':719-len(dif), 'first_difference':dif[0] if dif else None})
    profiles = []
    for d,r in zip(entries,replays):
        seat=d['seat']; milestones=[];land=[];build=[];hires=[]
        for i in range(1,720):
            pre=r['steps'][i-1][seat]['observation'];post=r['steps'][i][seat]['observation']
            f=pre['farms'][seat];g=post['farms'][seat];a=r['steps'][i][seat]['action']
            if f['unlocked_quadrants']!=g['unlocked_quadrants']:
                land.append({'step':i,'before':f['unlocked_quadrants'],'after':g['unlocked_quadrants']})
            for y,row in enumerate(g['tiles']):
                for x,t in enumerate(row):
                    old=f['tiles'][y][x]
                    if isinstance(t,dict) and t['kind'] in ['PASTURE','COOP'] and (not isinstance(old,dict) or old['kind']!=t['kind']):
                        build.append({'step':i,'kind':t['kind'],'xy':[x,y]})
            requested=sum(order[0]=='HIRE' for order in a['market'] if order)
            if requested:
                hires.append({'step':i,'requested':requested,'pre_cash':f['money'],'post_cash':g['money'],
                              'hands_before':len(f['hands']),'hands_after':len(g['hands']),
                              'note':'net state counts; daily reset may occur'})
        for i in [23,47,71,95,143,215,239,479,719]:
            o=r['steps'][i][seat]['observation'];f=o['farms'][seat]
            milestones.append({'step':i,'composition':composition(f),'cash':f['money'],
                               'quadrants':f['unlocked_quadrants'],'shops':o['town']['unlocked_shops']})
        profiles.append({'episode_id':d['episode']['id'],'submission_id':d['submission_id'],'seat':seat,
                         'opponent':d['opponent'],'opponent_submission_id':d['opponent_submission_id'],
                         'sha256':d['sha256'],'seed':d['seed'],'land_expansion':land,
                         'actual_structure_creation':build,'hire_requests_and_state_counts':hires,
                         'milestones':milestones,'opening_actions':actions[len(profiles)][:25]})
    return {'metrics':metrics,'pairs':pairs,'profiles':profiles,'context_selection':'fixed focus steps plus first full-action divergence each pre-action day; includes same-action controls', 'divergence_contexts':cases}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--manifest',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();entries=json.loads(args.manifest.read_text())
    out={'scope':'descriptive frozen sample, 3 per donor / 5 unique games; no causal or policy identification',
         'manifest_sha256':hashlib.sha256(args.manifest.read_bytes()).hexdigest(),
         'analyzer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'donors':{}}
    for name in sorted({d['team_name'] for d in entries}):
        out['donors'][name]=analyze_group([d for d in entries if d['team_name']==name])
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    for name,d in out['donors'].items():
        print(name,{k:v for k,v in d['metrics'].items() if k=='market_nonempty_union'})
        for p in d['profiles']:print(p['episode_id'],'land',p['land_expansion'],'day0',p['milestones'][0]['composition'])


if __name__=='__main__':main()
