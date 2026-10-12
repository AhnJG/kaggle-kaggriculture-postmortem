"""Read-only source/archived-result audit; no agent calls or new games.

Only writes audit.json beside this script. The 300 held-out tape outcomes are
excluded from every calculation; only their IDs are read from tape-split.json.
"""
import ast
import collections
import contextlib
import hashlib
import io
import json
import math
from pathlib import Path
import sys
import types

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
ENGINE = '.venv/lib/python3.13/site-packages/kaggle_environments/envs/kaggriculture/'
PATHS = {
    'engine': ENGINE + 'kaggriculture.py',
    'schema': ENGINE + 'kaggriculture.json',
    'v074': 'releases/round2-v074/main.py',
    'd157': 'releases/exp035-d157/main.py',
    'split': 'experiments/exp036_d157plus/tape-split.json',
    'meta': 'experiments/exp033_tapes/meta.json',
    'results': 'experiments/exp033_tapes/games-cloud.jsonl',
    'proposal': 'coordination/proposals/claude/20260927-ALTMECH-CODEX.md',
    'stage2_definition': 'experiments/exp036_d157plus/prep36.py',
    'judge_definition': 'experiments/exp036_d157plus/judge36.py',
}


def digest(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def global_names(code):
    names = set(code.co_names)
    for value in code.co_consts:
        if isinstance(value, types.CodeType):
            names.update(global_names(value))
    return sorted(names)


def source_inventory(label):
    path = PATHS[label]
    source = (ROOT / path).read_text()
    tree = ast.parse(source)
    wanted = ('_r37_', '_or2_', '_hd2_', '_race_', '_mpx_', '_s758_',
              '_cxtb_', '_v92_p_', '_hp_')
    functions = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name.startswith(wanted):
            functions.append(dict(name=node.name, start=node.lineno,
                                  end=node.end_lineno,
                                  ast_sha256=hashlib.sha256(ast.dump(node).encode()).hexdigest()))
    # Resolve saved parent function objects, not just repeated 'def agent' text.
    # This is source initialization only: no observation or policy invocation.
    namespace = {'__name__': '__altmech_source_audit__'}
    with contextlib.redirect_stdout(io.StringIO()):
        exec(compile(source, str(ROOT / path), 'exec'), namespace)
    entry = [v for v in namespace.values() if callable(v)][-1]
    pending = collections.deque([(entry, [entry.__name__])])
    seen = set()
    found = {}
    while pending:
        function, chain = pending.popleft()
        if id(function) in seen or not isinstance(function, types.FunctionType):
            continue
        seen.add(id(function))
        if function.__globals__ is not namespace:
            continue
        name = function.__name__
        if name.startswith(wanted):
            found.setdefault(name, dict(line=function.__code__.co_firstlineno, chain=chain))
        for global_name in global_names(function.__code__):
            child = namespace.get(global_name)
            if isinstance(child, types.FunctionType):
                pending.append((child, chain + [global_name]))
    return dict(entry=entry.__name__, functions=functions, global_reference_paths=found,
                limitation='Reference reachability is not measured branch activation or action effect.')


def main():
    before = {key: dict(path=path, sha256=digest(path)) for key, path in PATHS.items()}
    assert before['engine']['sha256'] == 'bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e'
    assert before['schema']['sha256'] == 'a82c89c1a2315b93f39775d8e025471a01b738647c9772658368ee6b1b6f4867'
    schema = json.loads((ROOT / PATHS['schema']).read_text())['observation']
    assert schema['farms']['shared'] and not schema['private']['shared']
    assert 'action' not in schema and 'orders' not in schema
    split = json.loads((ROOT / PATHS['split']).read_text())
    screen, holdout = set(split['screen']), set(split['holdout'])
    assert len(screen) == 50 and len(holdout) == 300 and not screen & holdout
    meta = {m['episode']: m for m in json.loads((ROOT / PATHS['meta']).read_text())}
    rows = {}
    for number, line in enumerate((ROOT / PATHS['results']).read_text().splitlines(), 1):
        r = json.loads(line)
        episode = int(r['opponent'][1:])
        if episode not in screen or r['vid'] not in ('P', 'd157'):
            continue
        key = (r['vid'], episode)
        assert key not in rows, ('duplicate', key)
        assert r['seed'] == meta[episode]['seed'] and r['seat'] == meta[episode]['seat']
        assert not 9000 <= r['seed'] <= 9599
        assert r['statuses'] == ['DONE', 'DONE'] and r['action_count'] == 719
        assert r['err'] is None and not r['agent_errors']
        rows[key] = dict(r, source_line=number)
    assert len(rows) == 100
    pairs = []
    for episode in sorted(screen):
        p, d = rows['P', episode], rows['d157', episode]
        seat = p['seat']
        pairs.append(dict(episode=episode, family=meta[episode]['fam'], seed=p['seed'], seat=seat,
                          P_score=p['score'], d157_score=d['score'],
                          own_cash_delta=d['rewards'][seat]-p['rewards'][seat],
                          opponent_cash_delta=d['rewards'][1-seat]-p['rewards'][1-seat],
                          P_line=p['source_line'], d157_line=d['source_line'],
                          action_sha_equal=p['act_sha'] == d['act_sha']))
    groups = {}
    for family in ['ALL'] + sorted({p['family'] for p in pairs}):
        group = [p for p in pairs if family == 'ALL' or p['family'] == family]
        n = len(group)
        def wdl(key):
            return [sum(p[key] == value for p in group) for value in (1, .5, 0)]
        groups[family] = dict(n=n, P_wdl=wdl('P_score'), d157_wdl=wdl('d157_score'),
            score_agreement=sum(p['P_score'] == p['d157_score'] for p in group),
            d157_improves=sum(p['d157_score'] > p['P_score'] for p in group),
            d157_worsens=sum(p['d157_score'] < p['P_score'] for p in group),
            own_cash_delta_mean=sum(p['own_cash_delta'] for p in group)/n,
            opponent_cash_delta_mean=sum(p['opponent_cash_delta'] for p in group)/n)
    a = [p['P_score'] for p in pairs]
    b = [p['d157_score'] for p in pairs]
    am, bm = sum(a)/len(a), sum(b)/len(b)
    den = math.sqrt(sum((x-am)**2 for x in a)*sum((x-bm)**2 for x in b))
    correlation = sum((x-am)*(y-bm) for x, y in zip(a, b))/den if den else None
    inventories = {label: source_inventory(label) for label in ('v074', 'd157')}
    function_maps = {label: {f['name']: f['ast_sha256'] for f in d['functions']}
                     for label, d in inventories.items()}
    identical = sorted(name for name, sha in function_maps['v074'].items()
                       if function_maps['d157'].get(name) == sha)
    after = {key: digest(path) for key, path in PATHS.items()}
    assert all(after[k] == v['sha256'] for k, v in before.items()), 'input changed during audit'
    result = dict(inputs=before, selection='EXP036 screen50; outcome-selected by EXP036, not an unbiased validation panel',
                  heldout_outcomes_used=0, new_games=0, policy_calls=0,
                  pairs=pairs, groups=groups, screen_score_pearson=correlation,
                  source_inventory=inventories, identical_function_AST=identical,
                  observable_fields=list(schema), input_hashes_unchanged=True)
    (OUT / 'audit.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(dict(check='PASS', new_games=0, valid_archived_rows=len(rows),
                          groups=groups, screen_score_pearson=correlation), ensure_ascii=False))


if __name__ == '__main__':
    main()
