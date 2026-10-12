import json,gzip,sys
sys.argv=['x','finalize_skip'];exec(open('experiments/exp041_top2400/prep41.py').read().split("if sys.argv[1]!='finalize':")[0])
E=json.load(open('analysis/d157_hosted_20260928/episodes_all.json'))
with open('experiments/exp041_top2400/d157feat.jsonl','w') as w:
    for e in E:
        if e['submission_label']!='d157':continue
        r=json.load(gzip.open(f"private_artifacts/d157_hosted_20260928/raw/{e['id']}.json.gz"));s=int(e['our_seat'])
        w.write(json.dumps(dict(episode=e['id'],result=e['result'],op_lb=e.get('op_lb_score'),me=feats(r,s),opp=feats(r,1-s)))+'\n')
print('ok')
