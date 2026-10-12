
# ==== EXP-060 MBR gate (Claude 2026-09-30). Base bytes above unchanged. ====
# At step 144, if the rival farm is identical to ours (mirror), use the route of this game's shop group from _MBR_TABLE (group from d157 effective route: 9->Y, 105->D, else S).
import json as _mbr_json
_MBR_TABLE = __TABLE__
_MBR_EFF = __EFF__
_MBR_EXTRA = _mbr_json.loads(__EXTRA__)
for _k, _v in _MBR_EXTRA.items():
    _IMPL.chassis.routes[int(_k)] = _v
_MBR_PARENT = [v for v in globals().values() if callable(v) and getattr(v, '__name__', '') != 'loads'][-1]
_MBR_S = {'restore': None}
_MBR_R = {'mirror': 0, 'switch': 0, 'err': 0}
def _mbr_same(a, b):
    return (a['tiles'] == b['tiles'] and list(a['farmer']) == list(b['farmer'])
            and [list(h) for h in a['hands']] == [list(h) for h in b['hands']]
            and list(a['unlocked_quadrants']) == list(b['unlocked_quadrants'])
            and abs(float(a['money']) - float(b['money'])) < 0.5)
def mbr_entry(obs, configuration=None):
    step = int(obs['step'])
    if _MBR_S['restore'] is not None and step != 144:
        k, v = _MBR_S['restore']
        if v is None: _V92_TABLE.pop(k, None)
        else: _V92_TABLE[k] = v
        _MBR_S['restore'] = None
    if step == 144:
        try:
            f = obs['farms']; p = int(obs['player'])
            if _mbr_same(f[p], f[1 - p]):
                _MBR_R['mirror'] += 1
                shops = tuple((obs['town']['unlocked_shops'] or [])[:2])
                r = _MBR_EFF.get('|'.join(shops))
                g = None if r is None else ('Y' if r == 9 else 'D' if r == 105 else 'S')
                if g in _MBR_TABLE:
                    _MBR_S['restore'] = (shops, _V92_TABLE.get(shops)); _V92_TABLE[shops] = _MBR_TABLE[g]; _MBR_R['switch'] += 1
        except Exception:
            _MBR_R['err'] += 1
    return _MBR_PARENT(obs, configuration)
mbr_entry.telemetry = _MBR_R
