
# ==== SLOT2-R gate (Claude 2026-09-29). Base bytes above unchanged. ====
# At step 144, if the rival farm is identical to ours (mirror of the same public tape), use route __R__ for this game.
_RG_PARENT = [v for v in globals().values() if callable(v)][-1]
_RG_ROUTE = __R__
_RG_S = {'restore': None}
_RG_R = {'mirror': 0, 'err': 0}
def _rg_same(a, b):
    return (a['tiles'] == b['tiles'] and list(a['farmer']) == list(b['farmer'])
            and [list(h) for h in a['hands']] == [list(h) for h in b['hands']]
            and list(a['unlocked_quadrants']) == list(b['unlocked_quadrants'])
            and abs(float(a['money']) - float(b['money'])) < 0.5)
def slot2r_entry(obs, configuration=None):
    step = int(obs['step'])
    if _RG_S['restore'] is not None and step != 144:
        k, v = _RG_S['restore']
        if v is None: _V92_TABLE.pop(k, None)
        else: _V92_TABLE[k] = v
        _RG_S['restore'] = None
    if step == 144:
        try:
            f = obs['farms']; p = int(obs['player'])
            if _rg_same(f[p], f[1 - p]):
                shops = tuple((obs['town']['unlocked_shops'] or [])[:2])
                _RG_S['restore'] = (shops, _V92_TABLE.get(shops)); _V92_TABLE[shops] = _RG_ROUTE; _RG_R['mirror'] += 1
        except Exception:
            _RG_R['err'] += 1
    return _RG_PARENT(obs, configuration)
slot2r_entry.telemetry = _RG_R
