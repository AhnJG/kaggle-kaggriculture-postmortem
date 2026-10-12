#!/usr/bin/env python3
"""Run the frozen P1b 13-episode manifest without early stopping."""

import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "experiments/results/p1_release_preflight"
AGENT = "experiments/results/p1_release_preflight/cleanroom/parent/main.py"
ENV = os.environ | {
    "OMP_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "VECLIB_MAXIMUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
}


CASES = [
    ("self_seed-7", AGENT, AGENT, 7, "both"),
    ("self_seed-1000", AGENT, AGENT, 1000, "both"),
    ("self_seed-1001", AGENT, AGENT, 1001, "both"),
    ("starter_seed-7_seat-0", AGENT, "starter", 7, "a"),
    ("starter_seed-7_seat-1", "starter", AGENT, 7, "b"),
    ("starter_seed-1000_seat-0", AGENT, "starter", 1000, "a"),
    ("starter_seed-1000_seat-1", "starter", AGENT, 1000, "b"),
    ("starter_seed-1001_seat-0", AGENT, "starter", 1001, "a"),
    ("starter_seed-1001_seat-1", "starter", AGENT, 1001, "b"),
    ("target_seed-1125321547_seat-0", AGENT, "tape:private_artifacts/tapes/Remielle_episode-108076177-actions.json", 1125321547, "a"),
    ("target_seed-1125321547_seat-1", "tape:private_artifacts/tapes/Remielle_episode-108076177-actions.json", AGENT, 1125321547, "b"),
    ("control_seed-1989066512_seat-0", AGENT, "tape:private_artifacts/tapes/today_episode-108079022-actions.json", 1989066512, "a"),
    ("control_seed-1989066512_seat-1", "tape:private_artifacts/tapes/today_episode-108079022-actions.json", AGENT, 1989066512, "b"),
]


def main():
    cells = OUT / "cells"
    cells.mkdir(exist_ok=False)
    records = []
    for name, a, b, seed, gate_agent in CASES:
        output = f"experiments/results/p1_release_preflight/cells/{name}.json"
        argv = [
            "python3", "tools/instrument.py", "--a", a, "--b", b,
            "--seeds", str(seed), "--steps", "720", "--time-agent", "both",
            "--gate-agent", gate_agent, "--json", output, "--require-pass",
        ]
        started = datetime.now(timezone.utc).isoformat()
        completed = subprocess.run(argv, cwd=ROOT, env=ENV, text=True, capture_output=True)
        ended = datetime.now(timezone.utc).isoformat()
        record = {
            "name": name,
            "argv": argv,
            "started_at_utc": started,
            "ended_at_utc": ended,
            "exit_code": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "json": output,
        }
        records.append(record)
        print(f"{name}: exit {completed.returncode}", flush=True)
    (OUT / "commands.json").write_text(
        json.dumps({"environment": {key: ENV[key] for key in sorted(ENV) if key.endswith("_NUM_THREADS") or key == "VECLIB_MAXIMUM_THREADS"}, "runs": records}, indent=2) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
