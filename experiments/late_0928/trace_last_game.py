"""Use the thirtieth and final cause-diagnosis game for a corrected d157 fill trace."""
import json
import pathlib

from cause_run import HERE, MANIFEST, play

row = next(r for r in MANIFEST["episodes"] if r["episode"] == 114044162)
result = play("d157", MANIFEST["agents"]["d157"], row)
(HERE / "cause_trace_d157_T114044162.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
print(result["key"], len(result["fills_after_575"]), result["rewards"], result["statuses"])
