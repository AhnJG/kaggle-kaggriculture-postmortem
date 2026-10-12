"""Freeze TOP2400 order experiment inputs and decision rules before games."""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
REL = "experiments/top2400_codex"
PARENT = "releases/exp035-d157/main.py"
CAND = f"{REL}/d157_order_swap.py"
EXPECTED_PARENT_SHA = "94a46c1196853577418bba1766fd347279aa8d213cea8812086d73c5f01c918e"
ENGINE_SHA = "bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e"


def sha(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def save(name, data):
    (OUT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def main():
    assert not (OUT / "prereg.json").exists(), "prereg is immutable"
    assert sha(PARENT) == EXPECTED_PARENT_SHA
    source = (ROOT / PARENT).read_bytes()
    suffix = (OUT / "order_swap_suffix.py.txt").read_bytes()
    (ROOT / CAND).write_bytes(source + suffix)
    compile((ROOT / CAND).read_bytes(), CAND, "exec")
    arms = [("d157", PARENT), ("swap", CAND)]
    split = json.loads((ROOT / "experiments/exp041_top2400/team-split.json").read_text())
    select, holdout = set(split["select_teams"]), set(split["holdout_teams"])
    assert len(holdout) == 5 and not select & holdout
    meta = list({m["episode"]: m for m in json.loads((ROOT / "experiments/exp041_top2400/meta.json").read_text())}.values())
    select_rows = [m for m in meta if m["team"] in select]
    holdout_rows = [m for m in meta if m["team"] in holdout]
    assert len(meta) == 743 and len(select_rows) == 595 and len(holdout_rows) == 148

    def tape_jobs(rows):
        return [[v, p, f"X{m['episode']}", f"experiments/exp041_top2400/tapes/X{m['episode']}.py", int(m["seed"]), int(m["our_seat"])]
                for m in rows for v, p in arms]

    select_jobs = tape_jobs(select_rows)
    holdout_jobs = tape_jobs(holdout_rows)
    u_meta = json.loads((ROOT / "experiments/exp039_camargin/meta-u.json").read_text())
    assert len(u_meta) == 136
    u_jobs = [[v, p, f"U{m['episode']}", f"experiments/exp039_camargin/tapes/U{m['episode']}.py", int(m["seed"]), int(m["seat"])]
              for m in u_meta for v, p in arms]
    t_meta = json.loads((ROOT / "experiments/exp033_tapes/meta.json").read_text())
    assert len(t_meta) == 350
    t_jobs = [[v, p, f"T{m['episode']}", f"experiments/exp033_tapes/tapes/T{m['episode']}.py", int(m["seed"]), int(m["seat"])]
              for m in t_meta for v, p in arms]
    base = "analysis/daily_scan/20260928/extracted/"
    family = [("D", "releases/public-dpnew-55be5d5f-exact/main.py"),
              ("HL63", base + "kaggriculture-harvest-ledger/main.py"),
              ("M2965", base + "2965-master-engine/main.py"),
              ("FJ1010", base + "farmer-john-and-the-idle-seller/main.py"),
              ("d157", PARENT)]
    other = [("O127", "releases/public-newmeta-127ed3e6-exact/main.py"),
             ("V074", "releases/round2-v074/main.py")]
    family_jobs = [[v, p, o, op, seed, seat]
                   for v, p in arms for o, op in family
                   for seed in range(15000, 15025) for seat in (0, 1)]
    guard_jobs = [[v, p, o, op, seed, seat]
                  for v, p in arms for o, op in other
                  for seed in range(15000, 15025) for seat in (0, 1)]
    with (ROOT / "analysis/d157_hosted_20260928/opponents.csv").open() as f:
        hosted = list(csv.DictReader(f))
    selected_losses = [r for r in hosted if r["submission_label"] == "d157"
                       and r["result"] == "L"
                       and 2400 <= float(r["op_lb_score"] or 0) < 2600
                       and r["op_team"] in select]
    assert len(selected_losses) == 20
    smoke_jobs = [[v, p, f"U{r['episode']}", f"experiments/exp039_camargin/tapes/U{r['episode']}.py", int(r["seed"]), int(r["seat"])]
                  for r in selected_losses for v, p in arms]
    categories = {"jobs-smoke.json": smoke_jobs, "jobs-select.json": select_jobs,
                  "jobs-holdout.json": holdout_jobs, "jobs-u.json": u_jobs,
                  "jobs-t.json": t_jobs, "jobs-family.json": family_jobs,
                  "jobs-guard.json": guard_jobs}
    for name, jobs in categories.items():
        assert all(j[4] not in range(9000, 9600) for j in jobs)
        assert len({(j[0], j[2], j[4], j[5]) for j in jobs}) == len(jobs)
        save(name, jobs)
    paths = sorted({job[1] for jobs in categories.values() for job in jobs}
                   | {job[3] for jobs in categories.values() for job in jobs})
    inputs = {p: sha(p) for p in paths}
    save("input-manifest.json", inputs)
    prereg = {
        "id": "TOP2400-CODEX-ORDER-0928", "hypothesis_id": "HYP-0016", "test_id": "TEST-TOP2400-ORDER-0928",
        "parent": PARENT, "parent_sha256": sha(PARENT), "candidate": CAND,
        "candidate_sha256": sha(CAND), "suffix_sha256": sha(f"{REL}/order_swap_suffix.py.txt"),
        "engine_sha256": ENGINE_SHA,
        "one_change": "For steps 144..718, swap an existing adjacent BUY_PRODUCT WHEAT then SELL WHEAT pair when pre-action shed WHEAT covers the SELL quantity and planned PICKUP; preserve both quantities and all other commands.",
        "fixed": ["d157 source bytes", "production and worker actions", "order quantities and count", "other market orders", "seeds, seats, tapes, opponents", "all decision gates"],
        "mechanism": "Selected top opponents often SELL WHEAT then BUY_PRODUCT WHEAT in one turn. Engine executes slots and quotes per unit; order reversal may depress the shared WHEAT quote during opposing SELL and recover the inventory in the later BUY slot. This tests d157's own order pair only, not a rival market tape graft.",
        "prior_evidence": f"{REL}/select_loss_fills.jsonl: 20 selected d157 losses exact-state parity; {REL}/select_loss_summary.json: top 30,891 filled WHEAT buys and 35,298 filled WHEAT sells, d157 6,687 and 10,920. Difference in requested counts alone is not causal.",
        "selection": {"team_split": "experiments/exp041_top2400/team-split.json", "select_teams": len(select), "select_tapes": len(select_rows), "holdout_teams": len(holdout), "holdout_tapes": len(holdout_rows), "holdout_access": "jobs constructed from metadata only; no holdout results inspected before candidate, parameters, jobs and rules freeze"},
        "smoke": {"jobs": len(smoke_jobs), "workers": 1, "maximum_games": 60,
                  "advance_if": "40/40 valid DONE/DONE, 719 candidate actions each, no agent errors, at least one candidate action SHA differs from paired d157; no tuning on smoke results"},
        "decision": {"invalid": "any missing/invalid/mismatched required job blocks PASS",
                     "select": "episode paired score delta mean, 10000 episode bootstrap resamples seed 9282400; lower 2.5 percentile strictly > 0",
                     "holdout": "after select PASS only, 5-team holdout tape point paired score delta strictly > 0; report per-team values, no retuning",
                     "U": "paired point delta >= 0 over all 136 d157 hosted opponent tapes",
                     "T": "paired point delta >= 0 over all 350 EXP-033 tapes",
                     "family": "pooled paired point delta >= 0 over D, HL63, M2965, FJ1010, d157 family arena; all 25 seeds both seats",
                     "O127": "candidate score >= d157 score - 0.02 over 25 seeds both seats",
                     "V074": "candidate score >= d157 score - 0.02 over 25 seeds both seats",
                     "D3": "1-worker measured candidate max step < 0.8 seconds; 719 actions; errors 0",
                     "success": "all gates true => LOCAL_SUPPORTED pending independent review; submission remains unauthorized",
                     "failure": "any numeric gate false => LOCAL_FAILED for this exact one-change artifact; no tuning against holdout"},
        "jobs_sha256": {name: sha(f"{REL}/{name}") for name in categories},
        "input_manifest_sha256": sha(f"{REL}/input-manifest.json"),
        "source_metadata_sha256": {p: sha(p) for p in ["experiments/exp041_top2400/meta.json", "experiments/exp041_top2400/team-split.json", "experiments/exp039_camargin/meta-u.json", "experiments/exp033_tapes/meta.json"]},
    }
    save("prereg.json", prereg)
    print("frozen", sha(f"{REL}/prereg.json"), "candidate", sha(CAND),
          "jobs", {k: len(v) for k, v in categories.items()})


if __name__ == "__main__":
    main()
