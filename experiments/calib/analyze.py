"""Read-only calibration summary from frozen local rows and hosted episode lists.

Run from the repository root: python3 experiments/calib/analyze.py
No new games, downloads, or holdout data are used.
"""

import collections
import hashlib
import json
import math
import statistics
from pathlib import Path


SOURCES = {
    "hosted_b": Path("analysis/hosted_20260929b/episodes_all.json"),
    "hosted_pm": Path("analysis/hosted_20260929pm/episodes_all.json"),
    "exp033": Path("experiments/exp033_tapes/games-kaggle.jsonl"),
    "exp039": Path("experiments/exp039_camargin/summary.json"),
    "exp041_kaggle": Path("experiments/exp041_top2400/games42-kaggle.jsonl"),
    "exp041_mac": Path("experiments/exp041_top2400/games42-mac.jsonl"),
    "exp051": Path("experiments/exp051_curpop/games.jsonl"),
}


def rows(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def score(result):
    return {"W": 1.0, "D": 0.5, "L": 0.0}[result]


def hosted_summary(items):
    counts = collections.Counter(item["result"] for item in items)
    lbs = [item["op_lb_score"] for item in items if item["op_lb_score"] is not None]
    return {
        "n": len(items),
        "wdl": {k: counts[k] for k in "WDL"},
        "score": round(sum(score(item["result"]) for item in items) / len(items), 6),
        "op_team_lb_median": round(statistics.median(lbs), 1) if lbs else None,
        "op_submission_ids": len({item["op_submissionId"] for item in items}),
        "first_game": items[0]["createTime"],
        "last_game": items[-1]["createTime"],
    }


def paired_summary(items, left, right):
    by_key = collections.defaultdict(dict)
    for item in items:
        if item["vid"] not in {left, right}:
            continue
        if item.get("err") or item.get("statuses") != ["DONE", "DONE"]:
            continue
        key = (item["opponent"], item["seed"], item["seat"])
        if item["vid"] in by_key[key]:
            raise ValueError(("duplicate", key, item["vid"]))
        by_key[key][item["vid"]] = item
    pairs = [v for v in by_key.values() if left in v and right in v]
    diffs = [v[left]["score"] - v[right]["score"] for v in pairs]
    n = len(diffs)
    mean = statistics.mean(diffs)
    se = statistics.stdev(diffs) / math.sqrt(n) if n > 1 else None
    return {
        "n": n,
        "left_score": round(statistics.mean(v[left]["score"] for v in pairs), 6),
        "right_score": round(statistics.mean(v[right]["score"] for v in pairs), 6),
        "delta": round(mean, 6),
        "pair_se": round(se, 6) if se is not None else None,
        "normal_95": [round(mean - 1.96 * se, 6), round(mean + 1.96 * se, 6)] if se else None,
        "flips": dict(collections.Counter(str(x) for x in diffs)),
    }


def main():
    hosted = json.loads(SOURCES["hosted_b"].read_text())
    previous = json.loads(SOURCES["hosted_pm"].read_text())
    assert len(hosted) == len({x["id"] for x in hosted})
    assert {x["id"] for x in previous} <= {x["id"] for x in hosted}
    groups = {
        label: sorted((x for x in hosted if x["submission_label"] == label), key=lambda x: x["createTime"])
        for label in ("c26", "d157")
    }
    result = {
        "input_sha256": {name: hashlib.sha256(path.read_bytes()).hexdigest() for name, path in SOURCES.items()},
        "hosted": {
            label: {
                "all": hosted_summary(items),
                "first30": hosted_summary(items[:30]),
                "last30": hosted_summary(items[-30:]),
                "first_third": hosted_summary(items[: len(items) // 3]),
                "last_third": hosted_summary(items[2 * len(items) // 3 :]),
            }
            for label, items in groups.items()
        },
        "new_since_pm": {
            label: hosted_summary(
                [x for x in groups[label] if x["id"] not in {y["id"] for y in previous}]
            )
            for label in groups
        },
        "common_op_submission_ids": len(
            {x["op_submissionId"] for x in groups["c26"]}
            & {x["op_submissionId"] for x in groups["d157"]}
        ),
        "local": {
            "exp033_d157_minus_v074": paired_summary(rows(SOURCES["exp033"]), "d157", "P"),
            "exp033_d157_minus_v171": paired_summary(rows(SOURCES["exp033"]), "d157", "V171"),
            "exp041_c26_minus_d157": paired_summary(
                rows(SOURCES["exp041_kaggle"]) + rows(SOURCES["exp041_mac"]), "c26", "d157"
            ),
            "exp041_v074_minus_d157": paired_summary(
                rows(SOURCES["exp041_kaggle"]) + rows(SOURCES["exp041_mac"]), "V074", "d157"
            ),
            "exp051_c26_minus_d157": paired_summary(rows(SOURCES["exp051"]), "c26", "d157"),
            "exp039_summary": {
                v["vid"]: {k: v[k] for k in ("tape", "tapeU", "fam", "abs_tape", "abs_U")}
                for v in json.loads(SOURCES["exp039"].read_text())["results"]
                if v["vid"] in {"d157", "c26"}
            },
        },
    }
    output = Path("experiments/calib/calibration.json")
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    print(output)
    for key, value in result["local"].items():
        print(key, value)
    print("hosted", {k: {part: v[part] for part in ("all", "last30")} for k, v in result["hosted"].items()})
    print("common_op_submission_ids", result["common_op_submission_ids"])


if __name__ == "__main__":
    main()
