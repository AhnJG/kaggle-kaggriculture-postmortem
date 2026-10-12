"""Read-only select replay diagnostic for shadow prediction; no arena selection."""
import contextlib
import gzip
import io
import json
import sys
import time
from collections import Counter
from pathlib import Path

from kaggle_environments.agent import get_last_callable
from kaggle_environments.utils import structify

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
ITEMS = ("WOOL", "MILK", "STRAWBERRY")


def events(action):
    return {o[1] for o in (action or {}).get("market", [])[:10]
            if isinstance(o, (list, tuple)) and len(o) >= 3 and o[0] == "SELL"
            and o[1] in ITEMS and int(o[2]) > 0}


def choose(n):
    split = json.loads((ROOT / "experiments/exp041_top2400/team-split.json").read_text())
    allowed = set(split["select_teams"])
    upper = {r["episode"]: r for r in map(json.loads, (ROOT / "analysis/exp046_predict/diag46.jsonl").open())}
    meta = json.loads((ROOT / "experiments/exp041_top2400/meta.json").read_text())
    by_team = {}
    for m in meta:
        if m["team"] in allowed and m["episode"] in upper:
            by_team.setdefault(m["team"], []).append(m)
    ordered = [by_team[t][k] for k in range(max(map(len, by_team.values())))
               for t in sorted(by_team) if k < len(by_team[t])]
    return ordered[:n], upper


def main(n):
    selected, upper = choose(n)
    counts = Counter()
    rows = []
    for m in selected:
        path = ROOT / f"private_artifacts/top2400_20260928/raw/{m['episode']}.json.gz"
        raw = json.load(gzip.open(path))
        with contextlib.redirect_stdout(io.StringIO()):
            agent = get_last_callable((OUT / "variants/hook.py").read_text(), path=str(OUT / "variants/hook.py"))
        ns = agent.__globals__
        cfg = structify(raw["configuration"])
        our = int(m["our_seat"])
        target = 1 - our
        c = Counter()
        max_step = 0.0
        for t in range(min(718, len(raw["steps"]) - 2)):
            obs = dict(raw["steps"][t][our]["observation"])
            public = raw["steps"][t][0]["observation"]
            for key in ("step", "day", "hour", "farms", "market", "town"):
                if key not in obs:
                    obs[key] = public[key]
            tic = time.perf_counter()
            with contextlib.redirect_stdout(io.StringIO()):
                agent(structify(obs), cfg)
            max_step = max(max_step, time.perf_counter() - tic)
            # The replay's market transition contains its recorded own action,
            # not the candidate's counterfactual action. Reconcile that input
            # so OR2's next-step market balance is meaningful on a fixed tape.
            st = ns["_OR2_STATE"].get(our)
            if st and st.get("prev"):
                own_orders = Counter()
                for order in (raw["steps"][t + 1][our]["action"] or {}).get("market", [])[:10]:
                    if isinstance(order, (list, tuple)) and len(order) >= 3 and order[0] == "SELL":
                        own_orders[order[1]] += max(0, int(order[2]))
                st["prev"]["own"] = dict(own_orders)
            pred = events(ns["_EXP047_PLAN"][t + 1])
            actual = events(raw["steps"][t + 2][target]["action"])
            c["tp"] += len(pred & actual)
            c["fp"] += len(pred - actual)
            c["fn"] += len(actual - pred)
        up = upper[m["episode"]]["events"]
        u_tp = sum(up.get(f"{i}|both", 0) for i in ITEMS)
        u_fp = sum(up.get(f"{i}|pred_only", 0) for i in ITEMS)
        u_fn = sum(up.get(f"{i}|act_only", 0) for i in ITEMS)
        c.update({"upper_tp": u_tp, "upper_fp": u_fp, "upper_fn": u_fn})
        counts.update(c)
        row = dict(episode=m["episode"], team=m["team"], counts=dict(c), max_step=max_step,
                   telemetry=dict(ns["_EXP047_REPORT"]))
        rows.append(row)
        print(m["episode"], m["team"], dict(c), round(max_step, 4), row["telemetry"], flush=True)
    def rp(prefix):
        tp, fp, fn = (counts[prefix + k] for k in ("tp", "fp", "fn"))
        return dict(recall=tp / (tp + fn) if tp + fn else None,
                    precision=tp / (tp + fp) if tp + fp else None,
                    tp=tp, fp=fp, fn=fn)
    result = dict(n=len(rows), episodes=[r["episode"] for r in rows], estimated=rp(""), upper=rp("upper_"),
                  max_step=max((r["max_step"] for r in rows), default=0), rows=rows)
    (OUT / f"diagnostic-{n}.json").write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print("SUMMARY", result["estimated"], result["upper"], result["max_step"], flush=True)


if __name__ == "__main__":
    main(int(sys.argv[1]))
