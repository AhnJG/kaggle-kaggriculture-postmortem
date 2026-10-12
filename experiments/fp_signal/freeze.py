"""Freeze the permitted hosted cohort before reading replay observations."""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "cohort.json"
assert not OUT.exists(), "refuse to overwrite frozen cohort"
source = ROOT / "analysis/c26_hosted_20260929/opponents.csv"
holdout_source = ROOT / "experiments/fp_robust/freeze.json"
holdout = set(json.loads(holdout_source.read_text())["holdout_episodes"])
rows = list(csv.DictReader(source.open(newline="")))
selected = [
    {k: row[k] for k in ("episode", "submission_id", "submission_label", "seed", "seat",
                            "result", "op_submissionId", "op_teamId", "endTime")}
    for row in rows
    if row["submission_id"] == "56607884"
    and row["submission_label"] == "d157"
    and row["is_55be"] == "True"
    and row["is_full"] == "False"
    and row["result"] in ("W", "L")
    and row["episode"] not in holdout
]
selected.sort(key=lambda x: (x["endTime"], x["episode"]))
assert len({x["episode"] for x in selected}) == len(selected)
assert all((ROOT / f"private_artifacts/c26_hosted_20260929/raw/{x['episode']}.json.gz").exists() for x in selected)
data = {
    "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
    "holdout_freeze_sha256": hashlib.sha256(holdout_source.read_bytes()).hexdigest(),
    "plan_sha256": hashlib.sha256((OUT.parent / "PLAN.md").read_bytes()).hexdigest(),
    "rows": selected,
}
OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
print("cohort", len(selected), "sha256", hashlib.sha256(OUT.read_bytes()).hexdigest())
