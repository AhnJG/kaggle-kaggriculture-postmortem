#!/usr/bin/env python3
"""원장 검사와 평가기 검증 게이트 (AGENTS §6, §7, §8).

사용:
  python3 tools/check.py ledger                       # 원장 형식·ID 검사
  python3 tools/check.py calibration --threshold 0.7  # 로컬 지표가 실전 순서를 맞히는가

표준 라이브러리만 쓴다.
"""
from __future__ import annotations

import argparse
import csv
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXP_ID = re.compile(r"^EXP-(\d{3,})$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
UTC = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2})?Z$")


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def check_experiments(rows: list[dict[str, str]], root: Path) -> list[str]:
    errors, numbers, seen = [], [], set()
    for i, r in enumerate(rows, start=2):
        eid = (r.get("exp_id") or "").strip()
        m = EXP_ID.match(eid)
        if not m:
            errors.append(f"experiments.csv:{i}: ID 형식 오류 {eid!r} (EXP-NNN)")
            continue
        if eid in seen:
            errors.append(f"experiments.csv:{i}: ID 중복 {eid}")
        seen.add(eid)
        numbers.append(int(m.group(1)))
        sha = (r.get("parent_sha256") or "").strip()
        if sha and not SHA256.match(sha):
            errors.append(f"experiments.csv:{i}: parent_sha256 형식 오류")
        created = (r.get("created_utc") or "").strip()
        if created and not UTC.match(created):
            errors.append(f"experiments.csv:{i}: created_utc 는 UTC ISO 형식 (예: 2026-09-01T12:00Z)")
        card = (r.get("card_path") or "").strip()
        if card and not (root / card).exists():
            errors.append(f"experiments.csv:{i}: card_path 없음 {card}")
    if numbers:
        missing = sorted(set(range(min(numbers), max(numbers) + 1)) - set(numbers))
        if missing:
            errors.append("experiments.csv: 결번 " + ", ".join(f"EXP-{n:03d}" for n in missing))
    return errors


def check_submissions(rows: list[dict[str, str]]) -> list[str]:
    errors, seen = [], set()
    for i, r in enumerate(rows, start=2):
        sid = (r.get("submission_id") or "").strip()
        if not sid:
            errors.append(f"submissions.csv:{i}: submission_id 비어 있음")
        elif sid in seen:
            errors.append(f"submissions.csv:{i}: submission_id 중복 {sid}")
        seen.add(sid)
        if not SHA256.match((r.get("artifact_sha256") or "").strip()):
            errors.append(f"submissions.csv:{i}: artifact_sha256 없음 또는 형식 오류")
        for col in ("submitted_utc", "observed_utc"):
            v = (r.get(col) or "").strip()
            if v and not UTC.match(v):
                errors.append(f"submissions.csv:{i}: {col} 는 UTC ISO 형식")
    return errors


def wilson_lower(k: int, n: int, z: float = 1.96) -> float:
    if n == 0:
        return 0.0
    p = k / n
    centre = p + z * z / (2 * n)
    spread = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (centre - spread) / (1 + z * z / n)


def calibration(rows: list[dict[str, str]]) -> dict[str, dict[str, float]]:
    """지표별로 '로컬 차이의 부호 = 실전 차이의 부호'인 쌍의 비율을 낸다. 어느 쪽이든 0 이면 제외."""
    out: dict[str, dict[str, float]] = {}
    for r in rows:
        try:
            local = float(r["local_a_minus_b"])
            hosted = float(r["hosted_a"]) - float(r["hosted_b"])
        except (KeyError, TypeError, ValueError):
            continue
        if local == 0 or hosted == 0:
            continue
        s = out.setdefault(r.get("metric") or "(none)", {"n": 0, "agree": 0})
        s["n"] += 1
        s["agree"] += int((local > 0) == (hosted > 0))
    for s in out.values():
        s["rate"] = s["agree"] / s["n"]
        s["wilson_lower"] = wilson_lower(int(s["agree"]), int(s["n"]))
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["ledger", "calibration"])
    ap.add_argument("--root", type=Path, default=ROOT)
    ap.add_argument("--threshold", type=float, default=0.7, help="순서 일치율 문턱 (STATE.md 에 적은 값)")
    ap.add_argument("--min-pairs", type=int, default=3)
    a = ap.parse_args(argv)
    ledger = a.root / "ledger"

    if a.command == "ledger":
        errors = check_experiments(read_rows(ledger / "experiments.csv"), a.root)
        errors += check_submissions(read_rows(ledger / "submissions.csv"))
        for e in errors:
            print("ERROR", e)
        print("ledger: OK" if not errors else f"ledger: {len(errors)} errors")
        return 1 if errors else 0

    stats = calibration(read_rows(ledger / "calibration.csv"))
    if not stats:
        print("calibration: 쌍 없음 — 이 지표로 탐색하지 않는다 (AGENTS §7)")
        return 1
    ok_all = True
    for metric, s in sorted(stats.items()):
        ok = s["n"] >= a.min_pairs and s["rate"] >= a.threshold
        ok_all &= ok
        print(f"{metric}: {int(s['agree'])}/{int(s['n'])} 일치 = {s['rate']:.2f} "
              f"(Wilson 95% 하한 {s['wilson_lower']:.2f}) → {'사용 가능' if ok else '탐색 금지'}")
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
