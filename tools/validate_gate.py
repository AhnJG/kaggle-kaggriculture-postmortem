#!/usr/bin/env python3
"""Validate a versioned gate JSON document."""

from __future__ import annotations

import argparse
import json
import sys

try:
    from gate_contract import validate
except ModuleNotFoundError:  # package import (e.g. unit tests)
    from tools.gate_contract import validate


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("json_path")
    args = parser.parse_args()
    try:
        with open(args.json_path, encoding="utf-8") as handle:
            doc = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"invalid JSON: {exc}", file=sys.stderr)
        raise SystemExit(3)
    errors = validate(doc)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        raise SystemExit(3)
    print("schema PASS")


if __name__ == "__main__":
    main()
