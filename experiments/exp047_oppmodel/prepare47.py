"""Freeze EXP-047 select jobs, excluding team holdout."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
variant = OUT / "variants/hook.py"
split = json.loads((ROOT / "experiments/exp041_top2400/team-split.json").read_text())
select = set(split["select_teams"])
holdout = set(split["holdout_teams"])
assert select.isdisjoint(holdout)
meta = list({m["episode"]: m for m in json.loads((ROOT / "experiments/exp041_top2400/meta.json").read_text())}.values())
chosen = [m for m in meta if m["team"] in select]
assert len(chosen) == 595 and all(m["team"] not in holdout for m in chosen)
jobs = [["hook", "experiments/exp047_oppmodel/variants/hook.py", f"X{m['episode']}",
         f"experiments/exp041_top2400/tapes/X{m['episode']}.py", m["seed"], m["our_seat"]]
        for m in chosen]
assert len({(j[2], j[4], j[5]) for j in jobs}) == len(jobs)
assert all(not 9000 <= int(j[4]) <= 9599 for j in jobs)
for name, data in (("jobs-A-kaggle.json", [j for i, j in enumerate(jobs) if i % 5 < 3]),
                   ("jobs-A-mac.json", [j for i, j in enumerate(jobs) if i % 5 >= 3]),
                   ("jobs-smoke.json", jobs[:4])):
    (OUT / name).write_text(json.dumps(data, ensure_ascii=False))
manifest = {
    "parent": "releases/exp035-d157/main.py",
    "parent_sha256": hashlib.sha256((ROOT / "releases/exp035-d157/main.py").read_bytes()).hexdigest(),
    "shadow": "releases/public-dpnew-55be5d5f-exact/main.py",
    "shadow_sha256": hashlib.sha256((ROOT / "releases/public-dpnew-55be5d5f-exact/main.py").read_bytes()).hexdigest(),
    "variant": "experiments/exp047_oppmodel/variants/hook.py",
    "variant_sha256": hashlib.sha256(variant.read_bytes()).hexdigest(),
    "source_lines": {
        "hook_gate": "releases/exp035-d157/main.py:487-488",
        "hook_logic": "releases/exp035-d157/main.py:662-690",
        "or2_stock": "releases/exp035-d157/main.py:4794-4832",
        "shadow_and_bridge": f"experiments/exp047_oppmodel/variants/hook.py:{len((ROOT / 'releases/exp035-d157/main.py').read_text().splitlines()) + 1}"
    },
    "approximation": "At step t, shadow forecasts step t+1 with current public farms, market and town unchanged, current OR2-derived rival stock, and empty hidden seeds/cargo.",
    "jobs": {name: {"count": len(json.loads((OUT / name).read_text())),
                    "sha256": hashlib.sha256((OUT / name).read_bytes()).hexdigest()}
             for name in ("jobs-A-kaggle.json", "jobs-A-mac.json", "jobs-smoke.json")},
    "selection": "EXP-041 prep42 select only; 595 games; 3:2 split; no holdout"
}
(OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
print({name: value["count"] for name, value in manifest["jobs"].items()})
