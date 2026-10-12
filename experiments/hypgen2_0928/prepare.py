"""Freeze one mechanism, all smoke/full jobs, and numerical gates before evaluation."""
import gzip
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
REL=str(OUT.relative_to(ROOT))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(name,obj):(OUT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')

def main():
    parent='releases/exp035-d157/main.py'
    pbytes=(ROOT/parent).read_bytes()
    assert sha(ROOT/parent)=='94a46c1196853577418bba1766fd347279aa8d213cea8812086d73c5f01c918e'
    candidate=REL+'/sheep_delivery.py'
    (ROOT/candidate).write_bytes(pbytes+(OUT/'sheep_delivery_suffix.py.txt').read_bytes())
    compile((ROOT/candidate).read_bytes(),candidate,'exec')
    agents=[('P',parent),('SHEEP_DELIVERY',candidate)]
    losses=[x for x in map(json.loads,(OUT/'hosted_features.jsonl').read_text().splitlines()) if x['metadata']['submission_label']=='d157' and x['metadata']['result']=='L']
    assert len(losses)==5
    smoke=[]
    for x in losses:
        m=x['metadata'];eid=m['episode'];raw=json.load(gzip.open(ROOT/x['raw']));seat=int(m['seat'])
        tape=[s[1-seat]['action'] for s in raw['steps'][1:]]
        tp=f'{REL}/T{eid}.py'
        (ROOT/tp).write_text('TAPE='+json.dumps(tape)+'\ndef agent(obs, configuration=None):\n    return TAPE[int(obs["step"])]\n')
        for v,p in agents:smoke.append([v,p,'T'+eid,tp,int(m['seed']),seat])
    opponents=[('V074','releases/round2-v074/main.py'),('O127','releases/public-newmeta-127ed3e6-exact/main.py'),('D','releases/public-dpnew-55be5d5f-exact/main.py'),('d157',parent)]
    for oid,op in opponents:
        for v,p in agents:
            for seat in [0,1]:smoke.append([v,p,oid,op,15080,seat])
    assert len(smoke)==26
    save('jobs-smoke.json',smoke)
    meta=json.loads((ROOT/'experiments/exp033_tapes/meta.json').read_text())
    guard=[g for g in json.loads((ROOT/'experiments/exp027_stage3/manifest.json').read_text())['guard'] if not g['sha256'].startswith('55be5d5f')]
    assert len(meta)==350 and len(guard)==23
    full=[]
    for v,p in agents:
        full += [[v,p,'T'+str(m['episode']),f"experiments/exp033_tapes/tapes/T{m['episode']}.py",m['seed'],m['seat']] for m in meta]
        for oid,op in opponents:
            full += [[v,p,oid,op,seed,seat] for seed in range(15100,15150) for seat in [0,1]]
        for g in guard:
            assert sha(ROOT/g['path'])==g['sha256']
            full += [[v,p,g['id'],g['path'],seed,seat] for seed in range(15200,15205) for seat in [0,1]]
    assert len(full)==1960
    save('jobs-full.json',full)
    # Fifteen D3 games per arm, serial cold loads; each of five seeds faces three opponents.
    runtime=[[v,p,oid,op,seed,seed%2] for v,p in agents for seed in range(15300,15305) for oid,op in opponents[:3]]
    save('jobs-d3.json',runtime)
    # Balanced deterministic shards; no cloud execution or upload by this preparation.
    for shard in range(5):save(f'jobs-kernel{shard}.json',full[shard::5])
    paths=sorted({j[1] for j in smoke+full+runtime}|{j[3] for j in smoke+full+runtime})
    assert all(j[4] not in range(9000,9600) for j in smoke+full+runtime)
    prereg=dict(id='HYPGEN2-SHEEP-DELIVERY',hypothesis_id='HYP-0020',test_id='TEST-HYPGEN2-0928-SHEEP-DELIVERY',
       parent=parent,parent_sha256=sha(ROOT/parent),candidate=candidate,candidate_sha256=sha(ROOT/candidate),
       one_change='In existing committed three-sheep crews, days 0..27: interleaved fertilizer collection -> mandatory FEED/CARE/HARVEST tour, WOOL delivery, then inherited fertilizer tour.',
       fixed=['no purchase/hire/land/target changes','no market policy edits','native workers unchanged','six-target compact crews unchanged','days 28..29 unchanged','all jobs and gates frozen'],
       rationale='Observed hosted 114208752 seat0: wool sold326 vs326; revenue51363 vs55027. Opponent defers collection, delivers18WOOL at450 versus parent453. Exact11 recorded-action replays passed all-step parity; source parent2019..2050 collects at each nearby tile before travel.',
       smoke=dict(jobs=26,total_mac_games_with_trace=37,workers=1,primary='T114208752',gate=['all 26 valid: DONE/DONE,719 calls,errors0','at least one changed action in primary pair','primary candidate margin greater than parent margin','no loss of existing live SHEEP in primary pair','primary own WOOL and FERTILIZER committed sale units both equal parent','each of four closed-loop smoke opponent score deltas >=0'],
                  failure='Any gate false: STOP; no edit, extra seeds, or full panel execution. Insufficient fields => INCONCLUSIVE, no advance.'),
       full=dict(jobs=1960,arms=2,per_arm=dict(tape=350,closed=400,guard=230),bootstrap_seed=928021,bootstrap_replicates=10000,
                 gates=['valid and exact input SHA for every job','open-loop paired score delta lower95>0, episode-cluster bootstrap','each tape family point delta>=-0.03; LB2200..2400 point delta>=0','each V074/O127/D/d157 closed score delta>=-0.03; 50 seed clusters per opponent','guard pooled delta>=-0.02; each guard delta>=-0.10','at least10 tape episodes: parent loss -> candidate win; Pearson score correlation recorded, no assumed diversity','D3 all pass'],
                 family_reference='experiments/exp033_tapes/meta.json',selection_bias='350 tapes are development data previously inspected, not an independent holdout; LB is team score, not opposing submission score.'),
       d3=dict(jobs=30,workers=1,engine_sha256='bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e',max_step_lt=.8,cold_load_plus_first_call_lt=.8,agent_cumulative_lt=30,exceptions_eq=0,action_count_eq=719,loaded_stress_max_lt=1.,loaded_stress='repeat these jobs on cloud with 5 concurrent kernels only after serial D3 passes; no Mac stress run'),
       outcome_rules=dict(success='All gates pass: LOCAL_SUPPORTED, independent review next, no submission.',failure='Any numeric gate fails: this implementation STOP.',inconclusive='Missing/invalid/nonidentical inputs: BLOCKED; do not merge partial results.'),
       files={p:sha(ROOT/p) for p in paths},jobs_sha256={n:sha(OUT/n) for n in ['jobs-smoke.json','jobs-full.json','jobs-d3.json']})
    save('prereg.json',prereg)
    print('frozen',sha(OUT/'prereg.json'),'candidate',prereg['candidate_sha256'],'smoke',len(smoke),'full',len(full))

if __name__=='__main__':main()
