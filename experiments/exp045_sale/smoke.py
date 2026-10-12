"""Run the frozen four-tape, one-worker EXP-045 v2 smoke panel."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "experiments/exp045_sale"
spec = importlib.util.spec_from_file_location("exp024_runner", ROOT / "experiments/exp024_round2/run.py")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)

manifest = json.loads((OUT / "manifest.json").read_text())
meta = {f"X{m['episode']}": m for m in json.loads((ROOT / "experiments/exp041_top2400/meta.json").read_text())}
split = json.loads((ROOT / "experiments/exp041_top2400/team-split.json").read_text())
baseline = {}
for path in (ROOT / "experiments/exp041_top2400/games42-kaggle.jsonl",
             ROOT / "experiments/exp041_top2400/games42-mac.jsonl"):
    for line in path.open():
        row = json.loads(line)
        if row["vid"] == "d157" and meta[row["opponent"]]["team"] in split["select_teams"]:
            baseline[row["opponent"]] = row
by_team = {}
for opp, row in sorted(baseline.items()):
    by_team.setdefault(meta[opp]["team"], row)
teams = sorted(by_team)
chosen = [by_team[teams[i]] for i in (0, 6, 12, 18)]
assert len(chosen) == 4 and len({meta[r['opponent']]['team'] for r in chosen}) == 4
assert all(r["statuses"] == ["DONE", "DONE"] and r["action_count"] == 719 for r in chosen)
(OUT / "smoke-panel.json").write_text(json.dumps([{
    "team": meta[r["opponent"]]["team"], "opponent": r["opponent"],
    "seed": r["seed"], "seat": r["seat"], "baseline_act_sha": r["act_sha"]
} for r in chosen], indent=2, ensure_ascii=False) + "\n")

existing = {}
results = OUT / "smoke.jsonl"
if results.exists():
    existing = {r["key"]: r for r in (json.loads(line) for line in results.open())}
with results.open("a") as output:
    for name, entry in manifest["variants"].items():
        for base in chosen:
            job = [name, entry["path"], base["opponent"],
                   f"experiments/exp041_top2400/tapes/{base['opponent']}.py",
                   base["seed"], base["seat"]]
            key = f"{name}|{base['opponent']}|{base['seed']}|{base['seat']}"
            if key in existing:
                continue
            row = runner.play(job)
            row["baseline_act_sha"] = base["act_sha"]
            row["changed_act"] = row["act_sha"] != base["act_sha"]
            output.write(json.dumps(row, separators=(",", ":")) + "\n")
            output.flush()
            print(name, base["opponent"], row["statuses"], round(row["max_step"], 3),
                  row["changed_act"], "ERR" if row["err"] or row["agent_errors"] else "OK", flush=True)
