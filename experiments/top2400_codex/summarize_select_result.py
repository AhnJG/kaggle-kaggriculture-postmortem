"""Descriptive audit of the completed select panel; no decision rule here."""
import hashlib
import json
from collections import Counter
from pathlib import Path

OUT = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    source = OUT / "games-select.jsonl"
    rows = [json.loads(line) for line in source.open()]
    assert len(rows) == 1190
    pairs = {}
    for row in rows:
        key = (row["opponent"], row["seed"], row["seat"])
        assert row["vid"] in ("d157", "swap")
        assert row["err"] is None and row["statuses"] == ["DONE", "DONE"]
        assert row["action_count"] == 719 and not row["agent_errors"]
        cell = pairs.setdefault(key, {})
        assert row["vid"] not in cell
        cell[row["vid"]] = row
    assert len(pairs) == 595 and all(set(pair) == {"d157", "swap"} for pair in pairs.values())
    score_delta = [pair["swap"]["score"] - pair["d157"]["score"] for pair in pairs.values()]
    margin_delta = [pair["swap"]["margin"] - pair["d157"]["margin"] for pair in pairs.values()]
    result = {
        "source_sha256": sha(source),
        "rows": len(rows),
        "pairs": len(pairs),
        "parent_wdl": {str(k): v for k, v in sorted(Counter(pair["d157"]["score"] for pair in pairs.values()).items())},
        "candidate_wdl": {str(k): v for k, v in sorted(Counter(pair["swap"]["score"] for pair in pairs.values()).items())},
        "score_delta_counts": {str(k): v for k, v in sorted(Counter(score_delta).items())},
        "action_sha_changed_pairs": sum(pair["swap"]["act_sha"] != pair["d157"]["act_sha"] for pair in pairs.values()),
        "margin_changed_pairs": sum(value != 0 for value in margin_delta),
        "margin_delta_mean": sum(margin_delta) / len(margin_delta),
        "margin_delta_min": min(margin_delta),
        "margin_delta_max": max(margin_delta),
        "candidate_max_step": max(pair["swap"]["max_step"] for pair in pairs.values()),
    }
    (OUT / "select_result_summary.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
