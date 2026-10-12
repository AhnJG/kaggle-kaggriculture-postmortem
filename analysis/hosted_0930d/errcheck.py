import kaggle,json,collections,sys
sid=int(sys.argv[1]) if len(sys.argv)>1 else 56694892
eps=[json.loads(e.to_json()) for e in kaggle.api.competition_list_episodes(sid)]
c=collections.Counter(); bad=[]
for e in eps:
    me=[a for a in e.get('agents',[]) if a.get('submissionId')==sid]
    st=(e.get('state'),e.get('type'),me[0].get('state') if me else None, me[0].get('reward') is None if me else None)
    c[st]+=1
    if me and (me[0].get('reward') is None or (me[0].get('state') not in (None,'DONE','AGENT_STATE_DONE'))): bad.append((e.get('id'),st))
print('episodes',len(eps)); print(c.most_common()); print('bad',bad[:10])
if eps: print(json.dumps(me[0])[:400] if me else '')
