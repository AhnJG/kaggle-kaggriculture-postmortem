"""Instrumented kaggriculture runner (engine 1.32.7, sha bc8a5487...).
Records per-player: harvest units by crop & day, sales units/revenue by item & day,
PLANT by crop & day, end-of-day farm composition, shop list by day.
Attribution: call-order cursor (FACTS 계측기 귀속 버그 수정 방식)."""
import json, collections
from kaggle_environments import make
from kaggle_environments.envs.kaggriculture import kaggriculture as K

CROPS = ["WHEAT", "CARROT", "STRAWBERRY", "TOMATO", "MELON"]
ANIMALS = ["COW", "SHEEP", "GOOSE"]


class Rec:
    def __init__(self):
        self.reset()

    def reset(self):
        self.cur = -1
        self.mcur = None
        self.day = 0
        self.harvest = [collections.defaultdict(int), collections.defaultdict(int)]  # (day,item)->units
        self.sell = [collections.defaultdict(int), collections.defaultdict(int)]
        self.rev = [collections.defaultdict(int), collections.defaultdict(int)]
        self.plant = [collections.defaultdict(int), collections.defaultdict(int)]
        self.snap = []  # per day: {pid: comp}
        self.shops = {}
        self.farms_ref = None


R = Rec()
_orig_apply = K._apply_unit_action
_orig_commit = K._commit_unit
_orig_market = K._process_market
_orig_eod = K._end_of_day


def _inv_total(inv):
    return dict(inv)


def apply_w(farm, private, idx, action, board_size, day, tpd, shed_capacity=100):
    if idx == 0:
        R.cur += 1
    pid = R.cur
    R.day = day
    op = action[0] if isinstance(action, list) and action else None
    if op == "HARVEST":
        invs = private.get("inventories", [])
        before = dict(invs[idx]) if idx < len(invs) else {}
        _orig_apply(farm, private, idx, action, board_size, day, tpd, shed_capacity)
        invs = private.get("inventories", [])
        after = invs[idx] if idx < len(invs) else {}
        for k, v in after.items():
            d = v - before.get(k, 0)
            if d > 0 and pid in (0, 1):
                R.harvest[pid][(day, k)] += d
        return
    if op == "PLANT" and pid in (0, 1):
        pos = K._farmer_position(farm, idx)
        before = None
        if pos is not None:
            t = farm["tiles"][pos[1]][pos[0]]
            before = json.dumps(t, sort_keys=True)
        _orig_apply(farm, private, idx, action, board_size, day, tpd, shed_capacity)
        if pos is not None:
            t = farm["tiles"][pos[1]][pos[0]]
            if json.dumps(t, sort_keys=True) != before and isinstance(t, dict) and t.get("kind") == "PLANT":
                R.plant[pid][(day, t.get("crop"))] += 1
        return
    return _orig_apply(farm, private, idx, action, board_size, day, tpd, shed_capacity)


def market_w(state, env):
    R.cur = -1
    R.farms_ref = [state[0].observation.farms[i] for i in range(len(state))]
    return _orig_market(state, env)


def commit_w(op, item, price, farm, private, market, shed_capacity=100):
    pid = None
    if R.farms_ref:
        for i, f in enumerate(R.farms_ref):
            if f is farm:
                pid = i
    ok = _orig_commit(op, item, price, farm, private, market, shed_capacity)
    if op == "SELL" and ok and pid is not None:
        R.sell[pid][(R.day, item)] += 1
        R.rev[pid][(R.day, item)] += price
    return ok


def comp(farm, private):
    crops = collections.Counter()
    animals = collections.Counter()
    for row in farm["tiles"]:
        for t in row:
            if isinstance(t, dict):
                if t.get("kind") == "PLANT":
                    crops[t.get("crop")] += 1
                a = t.get("animal")
                if a:
                    animals[a] += 1
    return dict(money=farm["money"], hands=len(farm.get("hands", [])), quads=len(farm.get("unlocked_quadrants", [])),
                crops=dict(crops), animals=dict(animals), shed=dict(private.get("shed", {})))


def eod_w(state, env, day):
    obs0 = state[0].observation
    snap = {pid: comp(obs0.farms[pid], state[pid].observation.private) for pid in range(len(state))}
    R.snap.append(snap)
    r = _orig_eod(state, env, day)
    R.shops[day + 1] = list(obs0.town["unlocked_shops"])
    return r


K._apply_unit_action = apply_w
K._commit_unit = commit_w
K._process_market = market_w
K._end_of_day = eod_w


def _check_commit_signature():
    import inspect
    return str(inspect.signature(_orig_commit))


def run(agents, seed):
    R.reset()
    env = make("kaggriculture", configuration={"seed": seed, "episodeSteps": 720})
    env.run(agents)
    last = env.steps[-1]

    def dd(d):
        return [[k[0], k[1], v] for k, v in sorted(d.items())]

    return dict(seed=seed, rewards=[s["reward"] for s in last], statuses=[s["status"] for s in last],
                shops={int(k): v for k, v in R.shops.items()},
                harvest=[dd(R.harvest[i]) for i in (0, 1)], sell=[dd(R.sell[i]) for i in (0, 1)],
                rev=[dd(R.rev[i]) for i in (0, 1)], plant=[dd(R.plant[i]) for i in (0, 1)],
                snap=[{str(k): v for k, v in s.items()} for s in R.snap], nsteps=len(env.steps))


def tape_agent(actions, seat):
    def agent(obs, cfg=None):
        t = obs["step"] + 1
        if t < len(actions):
            a = actions[t][seat]
            return a if a is not None else {}
        return {}
    return agent


_orig_weeds = K._spawn_weeds
WEEDLOG = []


def weeds_w(farm, board_size, weed_chance, rng):
    n = sum(1 for row in farm["tiles"] for t in row if t is None)
    WEEDLOG.append(n)
    return _orig_weeds(farm, board_size, weed_chance, rng)


K._spawn_weeds = weeds_w
