"""Run the preregistered runtime panel sequentially (exactly one worker)."""
import importlib.util
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("exp024_runner", ROOT / "experiments/exp024_round2/run.py")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
jobs = [tuple(job) for job in json.loads((HERE / "jobs-runtime.json").read_text())]
out = HERE / "games-runtime.jsonl"
done = set()
if out.exists():
    done = {json.loads(line)["key"] for line in out.read_text().splitlines() if line.strip()}
with out.open("a") as stream:
    for job in jobs:
        key = f"{job[0]}|{job[2]}|{job[4]}|{job[5]}"
        if key in done:
            continue
        result = runner.play(job)
        stream.write(json.dumps(result) + "\n")
        stream.flush()
        print(key, result["max_step"], flush=True)
