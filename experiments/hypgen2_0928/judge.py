"""Evaluate the frozen smoke contract. No extra games and no gate adjustment."""
import hashlib
import json
from pathlib import Path

OUT=Path(__file__).resolve().parent
EXPECTED_PREREG='d384cb94c69918383e30450472fba72c9c9389107aa5fde67f8bbbdccb75452d'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    assert sha(OUT/'prereg.json')==EXPECTED_PREREG
    prereg=json.loads((OUT/'prereg.json').read_text())
    jobs=json.loads((OUT/'jobs-smoke.json').read_text())
    rows=[json.loads(s) for s in (OUT/'games-smoke.jsonl').read_text().splitlines()]
    expected={f'{j[0]}|{j[2]}|{j[4]}|{j[5]}' for j in jobs}
    assert len(rows)==len(expected)==26 and {r['key'] for r in rows}==expected
    by={(r['vid'],r['opponent'],r['seed'],r['seat']):r for r in rows}
    pairs=[]
    for r in rows:
        if r['vid']!='P':continue
        c=by['SHEEP_DELIVERY',r['opponent'],r['seed'],r['seat']]
        pairs.append(dict(opponent=r['opponent'],seed=r['seed'],seat=r['seat'],parent_score=r['score'],candidate_score=c['score'],delta=c['score']-r['score'],parent_margin=r['margin'],candidate_margin=c['margin'],action_identical=r['act_sha']==c['act_sha'],candidate_changes=c['telemetry'].get('changed',0)))
    p=next(r for r in rows if r['vid']=='P' and r['opponent']=='T114208752')
    c=next(r for r in rows if r['vid']=='SHEEP_DELIVERY' and r['opponent']=='T114208752')
    def sold(r,item):return next(x['units'] for x in r['fills'] if x['op']=='SELL' and x['item']==item)
    boundary_valid=all(r['statuses']==['DONE','DONE'] and r['action_count']==719 and r['steps']==720 and not r['exceptions'] for r in rows)
    internal_errors=[dict(key=r['key'],errors=r['internal_errors']) for r in rows if r['internal_errors']]
    closed={oid:sum(p['delta'] for p in pairs if p['opponent']==oid)/2 for oid in ['V074','O127','D','d157']}
    gates=dict(all_26_boundary_valid=boundary_valid,all_26_internal_errors_zero=not internal_errors,
               primary_action_effect=c['telemetry']['changed']>0,primary_margin_improves=c['margin']>p['margin'],primary_sheep_preserved=c['final_sheep']==p['final_sheep'],
               primary_wool_units_preserved=sold(c,'WOOL')==sold(p,'WOOL'),primary_fertilizer_units_preserved=sold(c,'FERTILIZER')==sold(p,'FERTILIZER'),
               closed_each_delta_ge_zero=all(v>=0 for v in closed.values()))
    result=dict(verdict='PASS' if all(gates.values()) else 'FAIL',selected='SHEEP_DELIVERY' if all(gates.values()) else None,
                prereg_sha256=EXPECTED_PREREG,games_sha256=sha(OUT/'games-smoke.jsonl'),gates=gates,pairs=pairs,closed_deltas=closed,
                primary=dict(parent_margin=p['margin'],candidate_margin=c['margin'],margin_delta=c['margin']-p['margin'],own_cash_delta=c['rewards'][c['seat']]-p['rewards'][p['seat']],rival_cash_delta=c['rewards'][1-c['seat']]-p['rewards'][1-p['seat']],
                             parent_wool=sold(p,'WOOL'),candidate_wool=sold(c,'WOOL'),parent_fertilizer=sold(p,'FERTILIZER'),candidate_fertilizer=sold(c,'FERTILIZER')),
                internal_errors=internal_errors,total_new_games=37,trace_games=11,smoke_games=26,workers=1,remaining_budget_unused=3,
                full_execution_enabled=all(gates.values()),full_jobs=1960,d3_jobs=30,
                caveats=['Five hosted defeats selected for diagnosis; no field win-rate claim.','One closed-loop seed in both seats, inactive mechanism there, cannot establish non-inferiority.','Inherited caught errors are separate from zero boundary exceptions.','Fertilizer conservation alone fails independently of how inherited errors are interpreted.'])
    (OUT/'smoke-summary.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(verdict=result['verdict'],gates=gates,primary=result['primary']),ensure_ascii=False))

if __name__=='__main__':main()
