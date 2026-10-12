"""Apply frozen TOP2400 gates; open holdout outcomes only after select passes."""
import hashlib
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
PREREG_SHA = "578f171b6b14b22050f73c275666d901ac0bee97117f9f8aad33d052c008be8d"


def sha(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def read_panel(name, prereg):
    jobs_name = f"jobs-{name}.json"
    assert sha(f"experiments/top2400_codex/{jobs_name}") == prereg["jobs_sha256"][jobs_name]
    jobs = json.loads((OUT / jobs_name).read_text())
    path = OUT / f"games-{name}.jsonl"
    if not path.exists():
        return None, f"missing {path.name}"
    rows = {}
    for line in path.open():
        row = json.loads(line)
        if row["key"] in rows:
            return None, f"duplicate key {row['key']} in {path.name}"
        rows[row["key"]] = row
    keys = {f"{j[0]}|{j[2]}|{j[4]}|{j[5]}" for j in jobs}
    if rows.keys() != keys:
        return None, f"key mismatch {path.name}: expected {len(keys)}, actual {len(rows)}"
    for key, row in rows.items():
        if (row["err"] is not None or row["statuses"] != ["DONE", "DONE"]
                or row["score"] is None or row["agent_errors"]
                or row["action_count"] != 719):
            return None, f"invalid {key}"
    paired = {}
    for j in jobs:
        arm, _, opponent, _, seed, seat = j
        cell = (opponent, seed, seat)
        paired.setdefault(cell, {})[arm] = rows[f"{arm}|{opponent}|{seed}|{seat}"]
    if any(set(arms) != {"d157", "swap"} for arms in paired.values()):
        return None, f"unpaired {path.name}"
    return paired, None


def delta(paired):
    return [arms["swap"]["score"] - arms["d157"]["score"] for arms in paired.values()]


def mean(values):
    return sum(values) / len(values)


def lower95(values):
    rng = random.Random(9282400)
    n = len(values)
    boot = [sum(values[rng.randrange(n)] for _ in range(n)) / n for _ in range(10000)]
    boot.sort()
    return boot[249]


def main():
    assert sha("experiments/top2400_codex/prereg.json") == PREREG_SHA
    prereg = json.loads((OUT / "prereg.json").read_text())
    assert sha(prereg["parent"]) == prereg["parent_sha256"]
    assert sha(prereg["candidate"]) == prereg["candidate_sha256"]
    assert sha("experiments/top2400_codex/input-manifest.json") == prereg["input_manifest_sha256"]
    for path, expected in json.loads((OUT / "input-manifest.json").read_text()).items():
        assert sha(path) == expected, path
    for path, expected in prereg["source_metadata_sha256"].items():
        assert sha(path) == expected, path
    smoke, err = read_panel("smoke", prereg)
    if err:
        print(json.dumps({"verdict": "BLOCKED", "reason": err})); return
    changed = sum(arms["swap"]["act_sha"] != arms["d157"]["act_sha"] for arms in smoke.values())
    d3 = max(arms["swap"]["max_step"] for arms in smoke.values())
    if changed == 0 or d3 >= .8:
        print(json.dumps({"verdict": "LOCAL_FAILED", "smoke_changed_episodes": changed, "D3_max": d3})); return
    select, err = read_panel("select", prereg)
    if err:
        print(json.dumps({"verdict": "PENDING", "reason": err, "smoke_changed_episodes": changed, "D3_max": d3})); return
    select_d = delta(select)
    select_point, select_lower = mean(select_d), lower95(select_d)
    if select_lower <= 0:
        print(json.dumps({"verdict": "LOCAL_FAILED", "select_point": select_point, "select_lower95": select_lower,
                          "holdout": "UNOPENED", "smoke_changed_episodes": changed, "D3_max": d3})); return
    result = {"select_point": select_point, "select_lower95": select_lower,
              "smoke_changed_episodes": changed, "D3_max": d3}
    for name in ("u", "t", "family", "guard"):
        panel, err = read_panel(name, prereg)
        if err:
            print(json.dumps({"verdict": "PENDING", "reason": err, **result})); return
        if name == "guard":
            for opp in ("O127", "V074"):
                result[opp] = mean([arms["swap"]["score"] - arms["d157"]["score"]
                                    for (o, _, _), arms in panel.items() if o == opp])
        else:
            result[name] = mean(delta(panel))
    guard_pass = (result["u"] >= 0 and result["t"] >= 0 and result["family"] >= 0
                  and result["O127"] >= -.02 and result["V074"] >= -.02 and d3 < .8)
    if not guard_pass:
        print(json.dumps({"verdict": "LOCAL_FAILED", "holdout": "UNOPENED", **result})); return
    # All development and guard gates passed. Open holdout once, with no retuning.
    holdout, err = read_panel("holdout", prereg)
    if err:
        print(json.dumps({"verdict": "PENDING", "reason": err, **result})); return
    result["holdout_point"] = mean(delta(holdout))
    result["pass"] = result["holdout_point"] > 0
    result["verdict"] = "LOCAL_SUPPORTED" if result["pass"] else "LOCAL_FAILED"
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
