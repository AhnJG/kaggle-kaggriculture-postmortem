from tools.audit_p1c_replays import hire_observation


def replay(before,after,day_after=0):
    def row(n, action, day):
        return [{'observation':{'day':day,'hour':1,'farms':[{'money':100,'hands':[[4,4]]*n,'hires_today':n}]},
                 'action':{'market':action}}]
    return {'steps':[row(before,[],0),row(after,[['HIRE']]*5,day_after)]}


def test_hire_uses_previous_observation_not_next_turn():
    x=hire_observation(replay(0,5),0,1)
    assert x['filled']==5 and x['failed']==0
    x=hire_observation(replay(0,2),0,1)
    assert x['filled']==2 and x['failed']==3


def test_reset_is_unknown_not_five_failures():
    x=hire_observation(replay(2,0,day_after=1),0,1)
    assert x['failed'] is None
