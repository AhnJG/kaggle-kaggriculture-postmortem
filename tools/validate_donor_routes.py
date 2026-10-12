#!/usr/bin/env python3
"""Validate the frozen donor sample; no causal or policy-identification claim."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

from analyze_donor_routes import analyze_group

BASE = Path('experiments/results/top10_donor_routes_20260916')
MANIFEST = Path('experiments/results/top10_donor_20260916/donor_manifest.json')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(manifest, analysis_path):
    entries = json.loads(manifest.read_text())
    analysis = json.loads(analysis_path.read_text())
    checks = []

    def check(name, source, actual, expected):
        checks.append(dict(name=name, input=source, actual=actual, expected=expected,
                           result='PASS' if actual == expected else 'FAIL'))

    check('sample_size', str(manifest), [len(entries), len({d['episode']['id'] for d in entries})], [6, 5])
    check('manifest_identity', str(manifest), sha(manifest), analysis['manifest_sha256'])
    analyzer = Path(__file__).with_name('analyze_donor_routes.py')
    check('analyzer_identity', str(analyzer), sha(analyzer), analysis['analyzer_sha256'])
    raw = {}
    for d in entries:
        path = Path(d['path'])
        check('raw_identity_' + str(d['episode']['id']), str(path), sha(path), d['sha256'])
        if d['episode']['id'] not in raw:
            raw[d['episode']['id']] = json.loads(path.read_text())
    for team in sorted(analysis['donors']):
        group = [d for d in entries if d['team_name'] == team]
        saved = analysis['donors'][team]
        # Independently read primitive pre/action/post values, without context().
        mismatches = []
        for index, contexts in saved['divergence_contexts'].items():
            i = int(index)
            for d, c in zip(group, contexts):
                rows = raw[d['episode']['id']]['steps']; seat = d['seat']
                pre = rows[i-1][seat]['observation']; post = rows[i][seat]['observation']
                values = dict(pre_step=i-1, cash=pre['farms'][seat]['money'],
                    hands=len(pre['farms'][seat]['hands']), shops=pre['town']['unlocked_shops'],
                    prices=pre['market']['prices'], market_inventory=pre['market']['inventory'],
                    private=pre['private'], action=rows[i][seat]['action'],
                    opponent_previous_action_forensics_only=rows[i-1][1-seat]['action'],
                    post_cash=post['farms'][seat]['money'], post_hands=len(post['farms'][seat]['hands']),
                    post_private=post['private'])
                for field, value in values.items():
                    if c[field] != value:
                        mismatches.append([d['episode']['id'], i, field, c[field], value])
        check(team + '_alignment', {'raw_paths':[d['path'] for d in group],
              'indices':list(saved['divergence_contexts']), 'rule':'steps[i-1] -> steps[i].action -> steps[i]'}, mismatches, [])
        actions = [[row[d['seat']]['action'] for row in raw[d['episode']['id']]['steps'][1:]] for d in group]
        equal = sum(a['market'] == b['market'] == c['market'] for a,b,c in zip(*actions))
        nonempty = [(a,b,c) for a,b,c in zip(*actions) if any(x['market'] for x in (a,b,c))]
        check(team + '_issued_market', [d['path'] for d in group],
              [equal,len(nonempty),sum(a['market']==b['market']==c['market'] for a,b,c in nonempty)],
              [saved['metrics']['market']['all_three_equal'], saved['metrics']['market_nonempty_union']['steps'],
               saved['metrics']['market_nonempty_union']['all_three_equal']])
    maj = [d for d in entries if d['team_name']=='Majkel1337']
    def farm(d, i):
        return raw[d['episode']['id']]['steps'][i][d['seat']]['observation']['farms'][d['seat']]
    check('opening_cash', [d['path'] + ':steps[24]' for d in maj], [farm(d,24)['money'] for d in maj], [7,7,6])
    check('partial_hire', [d['path'] + ':steps[25]' for d in maj], [len(farm(d,25)['hands']) for d in maj], [4,4,3])
    check('recovery', [d['path'] + ':steps[26:28]' for d in maj],
          [[len(farm(d,26)['hands']),len(farm(d,27)['hands'])] for d in maj], [[4,4],[4,4],[3,4]])
    rows = raw[109675071]['steps']
    check('strawberry_request_without_seed_gain', 'episode 109675071 seat0 steps19/20',
          [rows[20][0]['action']['market'], rows[19][0]['observation']['farms'][0]['money'],
           rows[20][0]['observation']['farms'][0]['money'],
           rows[19][0]['observation']['private']['seeds']['STRAWBERRY'],
           rows[20][0]['observation']['private']['seeds']['STRAWBERRY']],
          [[['BUY_SEED','WHEAT',1],['BUY_SEED','STRAWBERRY',1]],37,27,0,0])
    m = [d for d in entries if d['team_name']=='M & M & P & Q']
    for d in m:
        rows = raw[d['episode']['id']]['steps']; seat = d['seat']
        has_goose = any(isinstance(t,dict) and t.get('animal')=='GOOSE'
                        for r in rows for row in r[seat]['observation']['farms'][seat]['tiles'] for t in row)
        check('goose_land_win_' + str(d['episode']['id']), d['path'],
              [has_goose, len(rows[-1][seat]['observation']['farms'][seat]['unlocked_quadrants']),
               rows[-1][seat]['reward'] > rows[-1][1-seat]['reward']], [True,4,True])
    initial = [{k:v for k,v in raw[d['episode']['id']]['steps'][0][d['seat']]['observation'].items()
                if k not in ('player','step','remainingOverageTime')} for d in m]
    check('initial_observation_equal', [d['path'] + ':steps[0]' for d in m], initial[0]==initial[1]==initial[2], True)
    same = [d for d in m if d['seat']==0]
    streams = [[r[0]['action'] for r in raw[d['episode']['id']]['steps'][1:]] for d in same]
    check('same_seat_first_difference', [d['path'] for d in same],
          next((i for i,(a,b) in enumerate(zip(*streams),1) if a!=b),None), 26)
    # Reproduction is a separate check, not an independent validation of the algorithm.
    regenerated = dict(scope=analysis['scope'], manifest_sha256=sha(manifest), analyzer_sha256=sha(analyzer),
        donors={name:analyze_group([d for d in entries if d['team_name']==name]) for name in sorted(analysis['donors'])})
    rebuilt = (json.dumps(regenerated,ensure_ascii=False,indent=2)+'\n').encode()
    check('regenerated_analysis_bytes', str(analysis_path), hashlib.sha256(rebuilt).hexdigest(), sha(analysis_path))
    return dict(schema_version=2, verdict='DESCRIPTIVE PASS' if all(c['result']=='PASS' for c in checks) else 'FAIL',
                scope='Observed sample only; causal effect and hidden policy remain unconfirmed.',
                analysis_sha256=sha(analysis_path), validator_sha256=sha(Path(__file__)), checks=checks)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, default=MANIFEST)
    parser.add_argument('--analysis', type=Path, default=BASE/'analysis.json')
    parser.add_argument('--output', type=Path, default=BASE/'validation.json')
    args = parser.parse_args()
    result = validate(args.manifest, args.analysis)
    result['command'] = ['python3', 'tools/validate_donor_routes.py', '--manifest', str(args.manifest),
                         '--analysis', str(args.analysis), '--output', str(args.output)]
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(result['verdict'], len(result['checks']), 'checks')
    return 0 if result['verdict']=='DESCRIPTIVE PASS' else 1


if __name__ == '__main__':
    sys.exit(main())
