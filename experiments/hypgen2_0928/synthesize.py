"""Reaggregate evidence and retain line-level references; never runs a game."""
import collections as C
import gzip
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(name,x):(OUT/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')

def main():
    features=[json.loads(l) for l in (OUT/'hosted_features.jsonl').read_text().splitlines()]
    pairs=json.loads((OUT/'tape_pairs.json').read_text())
    pairmap={str(x['meta']['episode']):x for x in pairs}
    traces=[json.loads(l) for l in (OUT/'trace_summary.jsonl').read_text().splitlines()]
    summary=json.loads((OUT/'smoke-summary.json').read_text())
    rows=[]
    for line,e in enumerate(features,1):
        m=e['metadata'];a,b=e['sides'];ta=a['checkpoints']['288']['tiles'];tb=b['checkpoints']['288']['tiles']
        dist=sum(abs(ta.get(k,0)-tb.get(k,0)) for k in set(ta)|set(tb))
        if m['submission_label']=='d157' or (m['result']=='L' and dist>10):
            rows.append(dict(episode=m['episode'],sub=m['submission_label'],result=m['result'],margin=int(m['margin']),label=m['label'],opponent_team=m['op_team'],opponent_submission=m['op_submissionId'],team_lb=m['op_lb_score'],
                             tile_distance_day12=dist,our_tiles=ta,opponent_tiles=tb,source=f'hosted_features.jsonl:{line}',originals=e['origins'],
                             tape_scores={v:r['score'] for v,r in pairmap.get(m['episode'],{}).get('rows',{}).items() if v in ['P','d157']}))
    save('field-reaggregation.json',rows)
    d157=[r for r in rows if r['sub']=='d157']
    bylb={}
    for band,predicate in [('all',lambda m:True),('team_LB_2200_2400',lambda m:m['op_lb'] is not None and 2200<=float(m['op_lb'])<2400)]:
        pp=[x for x in pairs if predicate(x['meta'])]
        bylb[band]={v:dict(n=len(pp),wdl=[sum(x['rows'][v]['score']==s for x in pp) for s in [1,.5,0]],score=sum(x['rows'][v]['score'] for x in pp)/len(pp)) for v in ['P','d157']}
    same={v:sum(x['rows'][v]['score']==x['rows']['d157']['score'] for x in pairs) for v in ['D','d053','b020','P']}
    save('field-totals.json',dict(unique_raw=len(features),input_window_sizes=[350,226],overlap=163,d157_wdl=dict(C.Counter(r['result'] for r in d157)),d157_n=len(d157),
                                tape=bylb,score_identity_vs_d157=same,live_loss_same_day12_composition=sum(r['result']=='L' and r['tile_distance_day12']==0 for r in d157)))
    source_specs=[
      ('se_tomato','analysis/daily_scan/20260922/extracted/kaggriculture-2887-score-fieldcraft-agent/main.py','https://www.kaggle.com/code/hakdevelopment/kaggriculture-2887-score-fieldcraft-agent','2026-09-22','Missing mirror_plan dependency; own SE garden at source422..447; no exact runnable package. No fallback graft.'),
      ('independent_consensus','analysis/daily_scan/20260926/extracted/kaggriculture-multi-route-farming-agent/main.py','https://www.kaggle.com/code/flexonafft/kaggriculture-multi-route-farming-agent','2026-09-26','Explicit 10C4S/8C6S/6C8S macro routes; G2602 existing closed-loop losses against both P and d157. No retuning.'),
      ('reactive_crop','analysis/daily_scan/20260922/extracted/farmcraft-kaggriculture-grandmaster/main.py','https://www.kaggle.com/code/datascikhan/farmcraft-kaggriculture-grandmaster','2026-09-22','Source204..224 returns hands=[]; no HIRE/BUY_ANIMAL action generator; no evidence for competitive strength.'),
      ('pioneers','analysis/daily_scan/20260924/extracted/pioneers-of-kaggle-town-candidate-2/main.py','https://www.kaggle.com/code/prvsiyan/pioneers-of-kaggle-town-candidate-2','2026-09-24','Do not infer lineage or score from title; existing tournament screen12/80, already failed. Supplemental historical context only.'),
    ]
    # Preserve URLs only when the daily scan's saved source reference confirms them.
    public=[]
    for name,path,url,collected,reason in source_specs:
        day=collected.replace('-','');lineage=json.loads((ROOT/f'analysis/daily_scan/{day}/lineage.json').read_text())
        slug=Path(path).parent.name;meta=next((x for x in lineage if x.get('slug')==slug),{})
        ref=meta.get('ref');verified_url='https://www.kaggle.com/code/'+ref if ref else None
        public.append(dict(id=name,path=path,sha256=sha(ROOT/path),source_url=verified_url,collection_directory_date=collected,declared_engine='N/A',reason=reason))
    save('public-candidates.json',public)
    mechanism=[]
    episode='114208752';e=next(x for x in features if x['metadata']['episode']==episode);raw=json.load(gzip.open(ROOT/e['raw']))
    for step in [439,440,443,444,447,450,453,454,455]:
        sides=[]
        for seat in [0,1]:
            pre=raw['steps'][step][seat]['observation'];post=raw['steps'][step+1][seat]['observation'];farm=raw['steps'][step][0]['observation']['farms'][seat];action=raw['steps'][step+1][seat]['action']
            pos=[farm['farmer']]+farm['hands'];cmd=[action['farmer']]+action['hands']
            sides.append(dict(seat=seat,actors=[dict(actor=i,position=pos[i],before_inventory=pre['private']['inventories'][i],action=cmd[i],after_inventory=post['private']['inventories'][i] if i<len(post['private']['inventories']) else None) for i in [12,13]],
                              before_shed_wool=pre['private']['shed']['WOOL'],after_shed_wool=post['private']['shed']['WOOL'],market=action['market']))
        mechanism.append(dict(episode=episode,action_step=step,pre_raw_index=step,action_and_post_raw_index=step+1,sides=sides))
    with (OUT/'rival-delivery-trace.jsonl').open('w') as f:
        for r in mechanism:f.write(json.dumps(r)+'\n')
    # Actual committed sales and purchases; requests are not fills.
    loss_table=[]
    for line,r in enumerate(traces,1):
        seat=r['our_seat'];by={(z['seat'],z['op'],z['item']):z for z in r['fills']}
        def get(s,op,item,k):return by.get((s,op,item),{}).get(k,0)
        loss_table.append(dict(episode=r['episode'],source=f'trace_summary.jsonl:{line}',parity_mismatches=r['parity_mismatches'],
             products={it:dict(own_units=get(seat,'SELL',it,'units'),opponent_units=get(1-seat,'SELL',it,'units'),own_revenue=get(seat,'SELL',it,'cash'),opponent_revenue=get(1-seat,'SELL',it,'cash')) for it in ['WOOL','MILK','TOMATO','STRAWBERRY','CARROT','FERTILIZER']},
             wheat_net=[get(s,'SELL','WHEAT','cash')-get(s,'BUY_PRODUCT','WHEAT','cash') for s in [seat,1-seat]]))
    save('loss-attribution.json',loss_table)
    # Baseline verification against original held actions/rewards in all five fresh replay probes.
    smoke=[json.loads(l) for l in (OUT/'games-smoke.jsonl').read_text().splitlines()]
    baseline=[]
    for r in smoke:
        if r['vid']!='P' or not r['opponent'].startswith('T'):continue
        ep=r['opponent'][1:];e=next(x for x in features if x['metadata']['episode']==ep);raw=json.load(gzip.open(ROOT/e['raw']))
        acts=[json.dumps(row[r['seat']]['action'],sort_keys=True,default=str) for row in raw['steps'][1:]]
        baseline.append(dict(episode=ep,exact_action_sha=hashlib.sha256('\n'.join(acts).encode()).hexdigest()==r['act_sha'],rewards_match=[row['reward'] for row in raw['steps'][-1]]==r['rewards']))
    save('baseline-parity.json',baseline)
    print('field',len(features),'trace',len(traces),'baseline',baseline,'smoke',summary['verdict'])

if __name__=='__main__':main()
