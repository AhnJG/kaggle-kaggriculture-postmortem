# Public-phenotype policy arbitration. Pick a parent policy once at the first
# CARROT2 decision and retain it through the game. No hidden labels or seeds.
_FP_B_PARENT = agent
_FP_B_MODE = {}
_FP_B_REPORT = {'calls': 0, 'c26': 0, 'd157': 0, 'errors': 0}

def _fp_b_classify(obs):
    seat = int(obs.get('player', 0))
    rival = obs['farms'][1-seat]
    count = {}
    for row in rival['tiles']:
        for tile in row:
            if isinstance(tile, dict):
                key = tile.get('crop') or tile.get('animal')
                if key:
                    count[key] = count.get(key, 0) + 1
    # The public 55be opening has 2 SHEEP, 4 COW, 12 MELON, 4 STRAWBERRY,
    # and 3 WHEAT at step 150 in every inspected development replay. This
    # deliberately uses a broad lower bound to tolerate neighboring variants.
    return 'c26' if (count.get('SHEEP', 0) >= 2 and
                     count.get('COW', 0) >= 4 and
                     count.get('MELON', 0) >= 10 and
                     count.get('STRAWBERRY', 0) >= 4) else 'd157'

def agent(obs, configuration=None):
    global _CA_MARGIN
    step = int(obs.get('step', 0))
    seat = int(obs.get('player', 0))
    if step == 0:
        _FP_B_MODE.clear()
        _FP_B_REPORT.update(calls=0, c26=0, d157=0, errors=0)
    _FP_B_REPORT['calls'] += 1
    if step >= 144 and seat not in _FP_B_MODE:
        try:
            _FP_B_MODE[seat] = _fp_b_classify(obs)
        except Exception:
            _FP_B_REPORT['errors'] += 1
            _FP_B_MODE[seat] = 'c26'
        _FP_B_REPORT[_FP_B_MODE[seat]] += 1
    _CA_MARGIN = -15.0 if _FP_B_MODE.get(seat) == 'd157' else -26.0
    return _FP_B_PARENT(obs, configuration)

kaggle_submission_agent = agent

def fp_b_entry(obs, configuration=None):
    return agent(obs, configuration)
