"""Independent arithmetic/identity audit of immutable EXP-018 per-game records."""
import csv
import hashlib
import json
import math
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'experiments/results/dp_loss_cause_20260925'
PANEL = ROOT / 'analysis/exp018_panel'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    freeze_path=OUT/'freeze.json'
    freeze=json.loads(freeze_path.read_text())
    checks=0
    for path,expected in freeze['sha256'].items():
        assert digest(ROOT/path)==expected,path
        checks+=1
    manifest=list(csv.DictReader((ROOT/'analysis/dp_hosted_20260924/opponents.csv').open()))
    expected=[r for r in manifest if r['match_full']=='True' and r['submission']!='56502662']
    assert len(expected)==47 and len({r['seed'] for r in expected})==47
    assert Counter(r['result'] for r in expected)=={'L':24,'W':23}
    summary=json.loads((PANEL/'summary.json').read_text())
    assert {r['episode'] for r in summary['panel']}=={r['episode'] for r in expected}
    differences=[];parents=[];candidates=[];changed=[];flips=regressions=0;max_seconds=0
    for row in expected:
        values=[]
        for label in ['parent','refresh']:
            path=OUT/'q2'/f"{row['episode']}-{label}.json"
            if not path.exists():path=PANEL/'games'/f"{row['episode']}-{label}.json"
            r=json.loads(path.read_text())
            assert r['freeze_sha256']==digest(freeze_path)
            assert r['card_sha256']==freeze['card_sha256']
            assert r['seed']==int(row['seed']) and r['seat']==int(row['dp_seat'])
            assert r['steps']==720 and r['statuses']==['DONE','DONE']
            assert not any(r['exceptions']) and not r['caught_errors']
            assert digest(ROOT/r['path'])==r['sha256']
            assert digest(ROOT/r['opponent'])==r['opponent_sha256']
            delta=r['rewards'][r['seat']]-r['rewards'][1-r['seat']]
            sc=(1 if delta>0 else 0 if delta<0 else .5)
            assert delta==r['margin'] and sc==r['score']
            if label=='parent':
                assert r['identity']==dict(actions=1438,states=1440,differences=[],passed=True)
                assert delta==float(row['margin'])
            else:
                assert r['sha256']==freeze['candidates']['refresh']['sha256']
                assert r['timing'][0]['calls']==719
                max_seconds=max(max_seconds,r['timing'][0]['max_seconds'])
            values.append(sc);checks+=12
        p,c=values;parents.append(p);candidates.append(c);differences.append(c-p)
        flips+=p==0 and c==1;regressions+=p==1 and c==0
        if p!=c:changed.append(row['episode'])
    mean=sum(differences)/47
    se=math.sqrt(sum((x-mean)**2 for x in differences)/(47*46))
    assert math.isclose(mean,summary['delta']) and math.isclose(se,summary['paired_se'])
    assert flips==summary['flipped_losses']==5 and regressions==summary['new_losses']==0
    assert mean>2*se
    direct=[];cells=set()
    for path in sorted((PANEL/'direct').glob('*.json')):
        r=json.loads(path.read_text());cells.add((r['seed'],r['seat']))
        assert r['freeze_sha256']==digest(freeze_path) and r['card_sha256']==freeze['card_sha256']
        assert r['sha256']==freeze['candidates']['refresh']['sha256']
        assert r['steps']==720 and r['statuses']==['DONE','DONE']
        assert not any(r['exceptions']) and not r['caught_errors']
        m=r['rewards'][r['seat']]-r['rewards'][1-r['seat']]
        sc=1 if m>0 else 0 if m<0 else .5
        assert m==r['margin'] and sc==r['score']
        assert r['timing'][0]['calls']==719
        max_seconds=max(max_seconds,r['timing'][0]['max_seconds'])
        direct.append(sc);checks+=7
    assert cells=={(s,p) for s in range(2400,2440) for p in (0,1)} and len(direct)==80
    direct_score=sum(direct)/80
    assert direct_score==summary['dp80_score']==.4875 and not summary['dp_floor_pass']
    assert not summary['eligible_success'] and max_seconds<.5
    assert math.isclose(max_seconds,summary['max_step_seconds'])
    q2=json.loads((OUT/'q2_refresh_summary.json').read_text())
    assert q2['flipped']==3 and len(q2['results'])==8
    assert not list((OUT/'q2').glob('*-carrot.json'))
    assert not (ROOT/'releases/dp0924-forecast-refresh-exp018').exists()
    result=dict(verdict='VERIFIED_NOT_ELIGIBLE_DP_FLOOR',frozen_input_count=len(freeze['sha256']),
                checks=checks,panel_parent_counts=dict(Counter(parents)),panel_candidate_counts=dict(Counter(candidates)),
                parent_action_matches=47*1438,parent_state_matches=47*1440,delta=mean,paired_se=se,
                flips=flips,regressions=regressions,changed_episodes=changed,dp80_counts=dict(Counter(direct)),
                dp80_score=direct_score,dp80_points=sum(direct),dp_required_points=40,max_step_seconds=max_seconds,
                panel_statistical_gate='PASS',overall_success_allowed=False,b2_allowed=False,
                card_sha256=freeze['card_sha256'],freeze_sha256=digest(freeze_path),
                runner_sha256=digest(ROOT/'tools/dp_counterfactual.py'),verifier_sha256=digest(Path(__file__)))
    target=OUT/'verification.json'
    if target.exists():assert json.loads(target.read_text())==result
    else:target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
