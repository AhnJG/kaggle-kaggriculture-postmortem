#!/usr/bin/env python3
"""Read-only replay audit: issued HIRE versus same-action hires_today delta."""
import hashlib
import json
from pathlib import Path


def hire_observation(replay, seat, index):
    pre=replay['steps'][index-1][seat]['observation']
    post=replay['steps'][index][seat]['observation']
    orders=replay['steps'][index][seat]['action'].get('market', [])
    requested=sum(isinstance(o,list) and bool(o) and o[0]=='HIRE' for o in orders[:10])
    if not requested:
        return None
    before=pre['farms'][seat]; after=post['farms'][seat]
    row=dict(action_row=index,pre_row=index-1,day=pre['day'],hour=pre['hour'],requested=requested,
             cash_before=before['money'],hands_before=len(before['hands']),hands_after=len(after['hands']))
    if pre['day']!=post['day']:
        return dict(row,filled=None,failed=None,reason='daily reset; success not identifiable from hires_today delta')
    filled=after['hires_today']-before['hires_today']
    assert 0<=filled<=requested,(index,filled,requested)
    assert len(after['hands'])-len(before['hands'])==filled
    return dict(row,filled=filled,failed=requested-filled)


def main():
    entries=[]
    for path in sorted(Path('evidence/raw/p1c_replays').glob('episode-*-replay.json')):
        raw=path.read_bytes();r=json.loads(raw);names=r['info']['TeamNames']
        assert names.count('Sian')==1,(path,names)
        seat=names.index('Sian');margin=r['rewards'][seat]-r['rewards'][1-seat]
        hires=[h for i in range(1,len(r['steps'])) if (h:=hire_observation(r,seat,i)) is not None]
        entries.append(dict(episode_id=r['info']['EpisodeId'],path=str(path),sha256=hashlib.sha256(raw).hexdigest(),
            seat=seat,opponent=names[1-seat],seed=r['info']['seed'],engine=r['module_version'],
            steps=len(r['steps']),statuses=r['statuses'],margin=margin,
            result='W' if margin>0 else 'L' if margin<0 else 'D',
            confirmed_hire_failed=sum(h['failed'] or 0 for h in hires),
            unknown_hire_turns=sum(h['failed'] is None for h in hires),hires=hires))
    totals={}
    for outcome in ['W','D','L']:
        group=[r for r in entries if r['result']==outcome]
        totals[outcome]=dict(games=len(group),with_confirmed_hire_failure=sum(r['confirmed_hire_failed']>0 for r in group),
                            failed_orders=sum(r['confirmed_hire_failed'] for r in group),
                            unknown_hire_turns=sum(r['unknown_hire_turns'] for r in group))
    output=dict(scope='77 locally available replays; time-window/submission linkage not independently established without source metadata',
        collection_window_claim='2026-09-16T16:46:04Z through 2026-09-17T16:46:04Z',
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        unique_episodes=len({r['episode_id'] for r in entries}),summary=totals,
        close_nonwins=[{k:r[k] for k in ['episode_id','seat','margin','opponent','result','confirmed_hire_failed']}
                      for r in entries if -500<=r['margin']<=0],
        entries=entries)
    assert len(entries)==len({r['episode_id'] for r in entries})==77
    dest=Path('experiments/results/p1c_20260918_audit/replay_audit.json')
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:output[k] for k in ['unique_episodes','summary','close_nonwins']},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
