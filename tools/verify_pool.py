#!/usr/bin/env python3
"""Verify an immutable replay pool by member count and content-set SHA-256."""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
from pathlib import Path


def pool_sha256(paths) -> str:
    """Hash sorted member content hashes so filenames and input order do not matter."""
    member_hashes = sorted(hashlib.sha256(Path(path).read_bytes()).hexdigest() for path in paths)
    return hashlib.sha256("".join(member_hashes).encode("ascii")).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--glob", required=True, dest="pattern")
    parser.add_argument("--expected-count", required=True, type=int)
    parser.add_argument("--expected-sha256", required=True)
    parser.add_argument("--json")
    args = parser.parse_args()

    paths = sorted(Path(path) for path in glob.glob(args.pattern) if Path(path).is_file())
    actual_hash = pool_sha256(paths)
    reasons = []
    if len(paths) != args.expected_count:
        reasons.append(f"count={len(paths)} expected={args.expected_count}")
    if actual_hash != args.expected_sha256:
        reasons.append(f"sha256={actual_hash} expected={args.expected_sha256}")
    result = {
        "verdict": "PASS" if not reasons else "FAILURE",
        "pattern": args.pattern,
        "count": len(paths),
        "sha256": actual_hash,
        "reasons": reasons,
        "files": [str(path) for path in paths],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.json:
        Path(args.json).write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    return 0 if not reasons else 2


if __name__ == "__main__":
    raise SystemExit(main())
