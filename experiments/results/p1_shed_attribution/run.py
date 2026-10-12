#!/usr/bin/env python3
"""EXP-011 fixed 13-cell execution and repeatable verification, from repo root."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import itertools
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path('experiments/results/p1_shed_attribution')
OLD = Path('experiments/results/p1_release_preflight')
FIELDS = ['shed_discarded', 'noop_actions', 'buy_failed', 'hire_failed', 'seed_blocked_plant',
          'hands_length_mismatch_count', 'shed_unsold', 'orders_truncated', 'exceptions']
CLASSES = ['|'.join(parts) for parts in itertools.product(
    ['ROOM_ZERO', 'ROOM_PARTIAL'], ['ADJACENT', 'REMOTE'], ['DEPOSIT_ATTEMPTED', 'NO_DEPOSIT_ATTEMPT'])]


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def identity():
    return [{'path': p, 'expected': expected, 'actual': sha(p)}
            for p, expected in read(ROOT/'freeze.json')['inputs'].items() if sha(p) != expected]


def verify(*, persist=False):
    checks = []
    def check(gate, source, actual, expected):
        checks.append(dict(gate=gate, source=source, actual=actual, expected=expected, passed=actual==expected))
    check('D1-a', 'freeze.json identities including tar/member/engine', identity(), [])
    logs = read(ROOT/'commands.json')['runs']
    check('D1-b', 'completed command count', len(logs), 13)
    records = []
    for run in logs:
        name = run['name']; doc = read(run['json']); previous = read(OLD/'cells'/f'{name}.json')
        r = doc['payload'][0]; old = previous['payload'][0]
        check('D1-b', name, [r['steps'], r['statuses']], [720, ['DONE', 'DONE']])
        check('D1-c', name+' rewards', r['rewards'], old['rewards'])
        check('D1-c', name+' gated seats', doc['gated_player_indices'], previous['gated_player_indices'])
        check('D1-c', name+' schema', doc['metric_schema_version'], 3)
        check('D1-c', name+' release verdict/exit', [doc['verdict'],run['exit_code']], ['FAILURE',2])
        check('R', name+' episode seconds', r['wall_seconds'] <= 960 and r['wall_seconds'] < 1200, True)
        for pid in doc['gated_player_indices']:
            source = f'{name}:p{pid}'; p = r['players'][pid]; baseline = old['players'][pid]
            check('D1-c', source, {k:p[k] for k in FIELDS}, {k:baseline[k] for k in FIELDS})
            check('R', source+' total_s', r['agent_ms_by_player'][pid]['total_s'] <= 623, True)
            events = p['drop_events']; counts = Counter(); nulls=0; invalid=0
            check('D2-a', source, sum(e['discarded_total'] for e in events), baseline['shed_discarded'])
            # 720 states mean 719 actions: day29 has no ordinary end-of-day call.
            check('D3', source+' EOD day coverage', [e['day'] for e in events], list(range(29)))
            for e in events:
                carried = sum(sum(inv.values()) for inv in e['carried_before'])
                check('D2-c', source+f":day{e['day']}", carried-sum(e['deposited'].values()), e['discarded_total'])
                check('D2-c', source+f":day{e['day']}:units", sum(e['discarded_by_unit']),e['discarded_total'])
                check('D2-c', source+f":day{e['day']}:losses", sum(x['quantity'] for x in e['losses']), e['discarded_total'])
                for loss in e['losses']:
                    nulls += sum(loss.get(k) is None for k in ['day','step','unit_index','item','shed_total_before','unit_last_op','unit_shed_adjacent_at_drop'])
                    label = '|'.join(('ROOM_ZERO' if loss['shed_total_before'] >= e['shed_capacity'] else 'ROOM_PARTIAL',
                                      'ADJACENT' if loss['unit_shed_adjacent_at_drop'] else 'REMOTE',
                                      'DEPOSIT_ATTEMPTED' if loss['unit_last_op'] in ('DROP','PLACE') else 'NO_DEPOSIT_ATTEMPT'))
                    invalid += int(loss['class'] not in CLASSES or loss['class'] != label)
                    counts[loss['class']] += loss['quantity']
            check('D3', source+' null fields', nulls, 0)
            check('D4', source+' invalid/nonexclusive class', invalid, 0)
            check('D4', source+' assigned units', sum(counts.values()), p['shed_discarded'])
            check('D4', source+' summary', p['drop_event_summary']['class_counts'], dict(sorted(counts.items())))
            records.append(dict(record=source, stratum='S2' if name.startswith('target_') else 'S1',
                                discarded=p['shed_discarded'], classes={c:counts[c] for c in CLASSES},
                                inday_drop=p['shed_discarded_inday_drop'], inday_place=p['shed_discarded_inday_place']))
    check('D1-b', 'gated records', len(records),16)
    check('D2-b', 'total discarded',sum(r['discarded'] for r in records),482)
    strata = {s:{c:sum(r['classes'][c] for r in records if r['stratum']==s) for c in CLASSES} for s in ('S1','S2')}
    check('D2-b', 'stratum totals', [sum(strata[s].values()) for s in ('S1','S2')], [64,418])
    winners = [c for c in CLASSES if strata['S1'][c]==max(strata['S1'].values())]
    dominant = winners[0] if len(winners)==1 else None
    unique_records = sum(r['classes'][dominant] > max(v for c,v in r['classes'].items() if c!=dominant)
                         for r in records) if dominant else 0
    share1 = strata['S1'][dominant]/64 if dominant else None
    share2 = strata['S2'][dominant]/418 if dominant else None
    supported = dominant and share1>=0.8 and share2>=0.8 and unique_records>=14
    verdict = 'BLOCKED_AMBIGUOUS_ROOT_CAUSE'
    if supported:
        verdict = ('REPAIR_AUTHORIZED' if dominant.startswith('ROOM_PARTIAL|') or
                   dominant=='ROOM_ZERO|ADJACENT|NO_DEPOSIT_ATTEMPT' else 'BLOCKED_STRATEGY_BOUNDARY')
    passed = all(c['passed'] for c in checks)
    result = dict(test_id='TEST-0011', hypothesis_id='HYP-0031', card_verdict='PASS' if passed else 'INVALID',
                  root_cause_verdict=verdict if passed else 'INVALID', release_verdict='FAILURE',
                  independent_review='PENDING_ANTIGRAVITY', records=records, strata=strata,
                  dominant_class=dominant, share_s1=share1, share_s2=share2, sole_top_records=unique_records,
                  checks=checks, evidence='LOCAL attribution only, not an intervention or hosted strength estimate')
    if persist:
        write(ROOT/'aggregate.json',result)
    print(result['card_verdict'], result['root_cause_verdict'], 'checks',len(checks), 'class',dominant,
          'shares',share1,share2,'sole_top',unique_records,flush=True)
    return 0 if passed else 1


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--verify-only',action='store_true');args=parser.parse_args()
    if args.verify_only:
        return verify()
    if (ROOT/'commands.json').exists():
        raise SystemExit('Refusing to overwrite executed batch; use --verify-only')
    assert not identity(), identity()
    plan=read(ROOT/'freeze.json'); env={**os.environ, **plan['environment'], 'PYTHONDONTWRITEBYTECODE':'1'}
    log=dict(environment=plan['environment'],runs=[])
    for run in plan['runs']:
        assert not identity(), identity()
        start=datetime.now(timezone.utc).isoformat()
        proc=subprocess.run(run['argv'],env=env,capture_output=True,text=True,timeout=1250)
        log['runs'].append(dict(**run,started_at_utc=start,ended_at_utc=datetime.now(timezone.utc).isoformat(),
                                exit_code=proc.returncode,stdout=proc.stdout,stderr=proc.stderr))
        write(ROOT/'commands.json',log)
        print(run['name'], 'exit',proc.returncode,flush=True)
        if proc.returncode not in (0,2):
            raise SystemExit('INVALID run; inspect commands.json')
    return verify(persist=True)


if __name__=='__main__':
    sys.exit(main())
