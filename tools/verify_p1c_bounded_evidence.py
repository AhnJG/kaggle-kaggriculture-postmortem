#!/usr/bin/env python3
"""Bounded read-only assertions; no game, policy, market or counterfactual run.

Only recorded unit actions at listed indices are checked with the locked engine.
The 77-file pass checks hashes, W/D/L and HIRE only, never remeasures all NOOPs.
JSON goes to stdout; callers choose a NEW result path.
"""
import contextlib
import copy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.audit_p1c_noops import audit_episode


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def observation(r, index, seat):
    # Shared fields only. NEVER fill private/player from the other seat.
    own = copy.deepcopy(r['steps'][index][seat]['observation'])
    for key in ('farms', 'market', 'town', 'day', 'hour', 'step'):
        if key not in own or own[key] is None:
            donors = [x['observation'][key] for x in r['steps'][index]
                      if key in x['observation'] and x['observation'][key] is not None]
            assert donors and all(v == donors[0] for v in donors)
            own[key] = copy.deepcopy(donors[0])
    assert 'private' in own and own['player'] == seat
    return own


def main():
    engine = ROOT / '.venv/lib/python3.13/site-packages/kaggle_environments/envs/kaggriculture/kaggriculture.py'
    assert digest(engine) == 'bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e'
    spec = importlib.util.spec_from_file_location('bounded_locked_engine', engine)
    K = importlib.util.module_from_spec(spec)
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        spec.loader.exec_module(K)
    checks, cases, unit_checks = [], {}, []

    def check(name, expected, actual):
        checks.append(dict(name=name, expected=expected, actual=actual,
                           result='PASS' if expected == actual else 'FAIL'))

    paths = sorted((ROOT / 'evidence/raw/p1c_replays').glob('episode-*-replay.json'))
    audit_path = ROOT / 'experiments/results/p1c_20260918_audit/replay_audit.json'
    prior = read(audit_path)
    protected = paths + [audit_path, engine, ROOT / 'tools/audit_p1c_noops.py',
                        ROOT / 'experiments/results/p1c_20260918_audit/noop_audit.json']
    hashes = {str(p.relative_to(ROOT)): digest(p) for p in protected}
    entries = {e['episode_id']: e for e in prior['entries']}
    selected = {110106409: [717, 718, 719], 109831239: [167, 718, 719],
                109856629: [718, 719], 109802471: [718, 719], 110024392: [2, 3]}
    replays, hire_events, failed_games = {}, [], {}
    summary = {k: dict(games=0, with_confirmed_hire_failure=0,
                       failed_orders=0, unknown_hire_turns=0) for k in ('W', 'D', 'L')}
    for path in paths:
        r = read(path)
        raw_sha = hashes[str(path.relative_to(ROOT))]
        eid = r['info']['EpisodeId']
        seat = r['info']['TeamNames'].index('Sian')
        assert r['info']['TeamNames'].count('Sian') == 1
        margin = r['rewards'][seat] - r['rewards'][1-seat]
        outcome = 'W' if margin > 0 else 'L' if margin < 0 else 'D'
        assert raw_sha == entries[eid]['sha256']
        failures = 0
        for i in range(1, len(r['steps'])):
            action = r['steps'][i][seat]['action']
            requested = sum(o[0] == 'HIRE' for o in action.get('market', [])[:10] if o)
            if not requested:
                continue
            before = observation(r, i-1, seat)
            after = observation(r, i, seat)
            assert before['day'] == after['day']
            a, b = before['farms'][seat], after['farms'][seat]
            actual = len(b['hands']) - len(a['hands'])
            assert 0 <= actual <= requested
            assert actual == b['hires_today'] - a['hires_today']
            failures += requested - actual
            hire_events.append(dict(episode=eid, seat=seat, raw_sha=raw_sha, index=i,
                                   requested=requested, filled=actual, failed=requested-actual))
        assert failures == entries[eid]['confirmed_hire_failed']
        if failures:
            failed_games[str(eid)] = failures
        summary[outcome]['games'] += 1
        summary[outcome]['failed_orders'] += failures
        summary[outcome]['with_confirmed_hire_failure'] += int(failures > 0)
        if eid in selected:
            replays[eid] = r
            for i in selected[eid]:
                cases[f'{eid}:{i}'] = dict(episode=eid, seat=seat, raw_sha=raw_sha,
                    action_index=i, pre_index=i-1, post_index=i,
                    pre=observation(r, i-1, seat), issued_action=r['steps'][i][seat]['action'],
                    post=observation(r, i, seat), opponent_action=r['steps'][i][1-seat]['action'],
                    submission='N/A', artifact='N/A', source_code='N/A')
    check('77 HIRE audit independently matches saved summary', prior['summary'], summary)
    check('failure episodes/orders', {'109899313': 8, '110024392': 2, '110041385': 3}, failed_games)
    check('unique episodes', 77, len({e['episode'] for e in hire_events}))
    check('close match margins', [-10, -92, 0, -422],
          [replays[e]['rewards'][entries[e]['seat']]-replays[e]['rewards'][1-entries[e]['seat']]
           for e in (110106409,109831239,109856629,109802471)])

    # Actual issued unit stage only; no interpreter, market or env.run invocation.
    # Sequential per-unit before/after avoids attributing whole-turn deltas to a unit.
    for eid, index in ((110106409, 718), (109802471, 718), (109831239, 167),
                       (109831239, 718), (109831239, 719)):
        c = cases[f'{eid}:{index}']; s = c['seat']; r = replays[eid]
        farm, private = copy.deepcopy(c['pre']['farms'][s]), copy.deepcopy(c['pre']['private'])
        actions = [c['issued_action']['farmer']] + c['issued_action']['hands']
        demand = {}
        for a in actions:
            if a and a[0] == 'PLANT': demand[a[1]] = demand.get(a[1], 0) + 1
        blocked = {crop for crop, n in demand.items() if n > private['seeds'].get(crop, 0)}
        for u, a in enumerate(actions):
            permitted = ['PASS'] if a[0] == 'PLANT' and a[1] in blocked else a
            before = copy.deepcopy(dict(farm=farm, private=private))
            K._apply_unit_action(farm, private, u, permitted, r['configuration']['boardSize'],
                                 c['pre']['day'], r['configuration']['turnsPerDay'], r['configuration']['shedCapacity'])
            if a[0] == 'PLACE' or (eid == 109831239 and index == 167 and u == 2):
                unit_checks.append(dict(episode=eid, seat=s, raw_sha=c['raw_sha'], action_index=index,
                    unit_index=u, issued=a, before=before, immediate_after=copy.deepcopy(dict(farm=farm, private=private))))
        c['actual_unit_stage_shed'] = private['shed']
        check(f'{eid}:{index} unit inventory matches raw post', c['post']['private']['inventories'], private['inventories'])
        check(f'{eid}:{index} tiles match raw post', c['post']['farms'][s]['tiles'], farm['tiles'])
    for eid in (110106409, 109802471):
        c = cases[f'{eid}:718']
        milk = [u for u in unit_checks if u['episode']==eid and u['issued']==['PLACE','MILK',1000]]
        deposits = [u['immediate_after']['private']['shed']['MILK']-u['before']['private']['shed']['MILK'] for u in milk]
        check(f'{eid}:718 PLACE MILK deposits by unit, not failure', [3, 15], deposits)
        check(f'{eid}:718 MILK available before market / after', [18, 0],
              [c['actual_unit_stage_shed']['MILK'], c['post']['private']['shed']['MILK']])
    c = cases['109831239:718']
    check('109831239:718 crops sold; not left to end', [5, 3, 0, 0],
          [c['actual_unit_stage_shed'][k] for k in ('STRAWBERRY','WHEAT')] +
          [c['post']['private']['shed'][k] for k in ('STRAWBERRY','WHEAT')])
    c = cases['109831239:719']
    check('109831239:719 real remaining WOOL', [10, [['SELL','WOOL',8]], 2],
          [c['pre']['private']['shed']['WOOL'], c['issued_action']['market'], c['post']['private']['shed']['WOOL']])
    c = cases['109856629:718']; f=c['pre']['farms'][0]
    positions = [f['farmer']] + f['hands']
    carriers = [u for u,inv in enumerate(c['pre']['private']['inventories']) if any(inv.get(k,0) for k in ('WOOL','MILK','EGG'))]
    check('109856629:718 proposed product DROP is unavailable at pre-state',
          [[3,5],[5,3],[6,4]], [positions[u] for u in carriers])
    check('109856629:718 none of product carriers can DROP', [False]*3,
          [K._is_shed_adjacent(positions[u],10) for u in carriers])
    c = cases['109856629:719']
    check('109856629:719 WOOL price change, not fixed sale quote', [154,31],
          [c['pre']['market']['prices']['WOOL'],c['post']['market']['prices']['WOOL']])
    c = cases['109802471:718']
    check('109802471:718 already behind; marginal change only -3',
          [[117682,118101],[121923,122345],[4241,4244]],
          [[f['money'] for f in c[k]['farms']] for k in ('pre','post')] +
          [[c['post']['farms'][s]['money']-c['pre']['farms'][s]['money'] for s in (0,1)]])
    c = cases['110024392:2'];s=c['seat']
    check('prior Codex rebuttal row2 HIRE succeeds', [0,5], [len(c[k]['farms'][s]['hands']) for k in ('pre','post')])
    c = cases['110024392:3']
    check('prior Codex rebuttal row3 WEST succeeds', [[5,4],[4,4]], [c[k]['farms'][s]['hands'][1] for k in ('pre','post')])

    # Audit function on a single REAL transition, plus clearly synthetic controls.
    # These exercise its definition, not a new engine/game or a replacement audit.
    r = replays[109831239]; c=cases['109831239:167']; s=c['seat']
    mini = copy.deepcopy(r); mini['steps'] = copy.deepcopy(r['steps'][166:168])
    with tempfile.TemporaryDirectory(prefix='p1c-definition-') as td:
        path=Path(td)/'fixture.json'
        path.write_text(json.dumps(mini)); real=audit_episode(path)
        check('NOOP counter misses real WATER on empty tile, shed changed elsewhere', 0, real['noop_by_op'].get('WATER',0))
        unit = next(u for u in unit_checks if u['episode']==109831239 and u['action_index']==167 and u['unit_index']==2)
        check('real WATER is immediate engine no-op', unit['before'], unit['immediate_after'])
        synthetic = copy.deepcopy(mini)
        pre=synthetic['steps'][0][s]['observation'];post=copy.deepcopy(pre)
        pre['farms'][s]['hands'][0]=[0,0];post['farms'][s]['hands'][0]=[0,0]
        synthetic['steps'][1][s]['observation']=post
        synthetic['steps'][1][s]['action']={'farmer':['PASS'],'hands':[['WEST']],'market':[]}
        path.write_text(json.dumps(synthetic))
        check('SYNTHETIC blocked move is counted despite reported exclusion', {'WEST':1}, audit_episode(path)['noop_by_op'])
        synthetic['steps'][1][s]['action']={'farmer':['WATER'],'hands':[],'market':[]}
        path.write_text(json.dumps(synthetic))
        check('SYNTHETIC farmer is not examined', 0, audit_episode(path)['true_noop'])
    # Raw seat1 lacks step, but retains its own private and shared farm data.
    check('seat1 step reconstructed without copying seat0 private',
          [False, 717, r['steps'][717][1]['observation']['private']],
          ['step' in r['steps'][717][1]['observation'], observation(r,717,1)['step'], observation(r,717,1)['private']])
    check('protected inputs remain unchanged', hashes, {p:digest(ROOT/p) for p in hashes})
    # Large equality operands stay in cases; retain compact PASS evidence in checks.
    for c in checks:
        if c['result']=='PASS' and len(json.dumps(c['actual']))>1500:
            c['actual']=c['expected']={'equal_json_sha256':hashlib.sha256(json.dumps(c['actual'],sort_keys=True).encode()).hexdigest()}
    output=dict(script_sha256=digest(Path(__file__)), engine_sha256=digest(engine),
                input_sha256=hashes, assertions=checks, cases=cases, recorded_unit_checks=unit_checks,
                hire_summary=summary, hire_events=hire_events,
                scope='Actual recorded actions only; NOOP definition checked on one real row and synthetic fixtures; no games or counterfactual execution')
    print(json.dumps(output,ensure_ascii=False,indent=2))
    return int(any(c['result']=='FAIL' for c in checks))


if __name__=='__main__':
    raise SystemExit(main())
