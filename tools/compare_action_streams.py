#!/usr/bin/env python3
"""Compare player action streams emitted by tools/instrument.py."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from instrument import action_difference, action_stream_sha256
except ModuleNotFoundError:
    from tools.instrument import action_difference, action_stream_sha256


def load_stream(path: Path, report_index: int, player: int) -> list:
    document = json.loads(path.read_text(encoding="utf-8"))
    reports = document.get("payload", [document])
    return reports[report_index]["action_streams"][player]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--left", type=Path, required=True)
    parser.add_argument("--right", type=Path, required=True)
    parser.add_argument("--left-report-index", type=int, default=0)
    parser.add_argument("--right-report-index", type=int, default=0)
    parser.add_argument("--left-player", type=int, choices=(0, 1), required=True)
    parser.add_argument("--right-player", type=int, choices=(0, 1), required=True)
    parser.add_argument("--json")
    args = parser.parse_args()

    left = load_stream(args.left, args.left_report_index, args.left_player)
    right = load_stream(args.right, args.right_report_index, args.right_player)
    result = action_difference(left, right)
    result.update({
        "left_actions": len(left),
        "right_actions": len(right),
        "left_sha256": action_stream_sha256(left),
        "right_sha256": action_stream_sha256(right),
    })
    output = json.dumps(result, ensure_ascii=False, indent=2)
    print(output)
    if args.json:
        Path(args.json).write_text(output + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
