#!/usr/bin/env python3
"""Validate the hypothesis ledger and optional experiment-card links."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ID_RE = re.compile(r"^## (HYP-\d{4})$")
CARD_ID_RE = re.compile(r"(?m)^hypothesis_id:\s*(HYP-\d{4})\s*$")
CARD_TEST_RE = re.compile(r"(?m)^test_id:\s*(TEST-[A-Z0-9-]+)\s*$")
SUBMISSION_ID_RE = re.compile(r"\b\d{8}\b")
REQUIRED_FIELDS = (
    "쉬운 설명",
    "주장",
    "출처 수준",
    "출처",
    "엔진",
    "실험",
    "로컬 결과",
    "Hosted 결과",
    "상태",
    "유효 범위",
    "다음 행동",
)
ALLOWED_LEVELS = {
    "OFFICIAL", "ENGINE", "HOSTED", "LOCAL", "COMMUNITY",
    "INFERENCE", "HYPOTHESIS",
}
ALLOWED_STATUSES = {
    "SOURCE_CLAIM", "PLANNED", "ENGINE_CONFIRMED", "LOCAL_SUPPORTED",
    "LOCAL_FAILED", "HOSTED_SUPPORTED", "HOSTED_FAILED", "INCONCLUSIVE",
    "PENDING_HOSTED", "RETRACTED",
}


def parse_ledger(text: str) -> tuple[dict[str, dict[str, str]], list[str]]:
    errors: list[str] = []
    if not re.search(r"(?m)^schema_version:\s*1\s*$", text):
        errors.append("schema_version must be 1")

    entries: dict[str, dict[str, str]] = {}
    current_id: str | None = None
    for line_no, line in enumerate(text.splitlines(), 1):
        match = ID_RE.match(line)
        if match:
            current_id = match.group(1)
            if current_id in entries:
                errors.append(f"line {line_no}: duplicate id {current_id}")
            else:
                entries[current_id] = {}
            continue
        if current_id is None or not line.startswith("- ") or ":" not in line:
            continue
        key, value = line[2:].split(":", 1)
        key, value = key.strip(), value.strip()
        if key in entries[current_id]:
            errors.append(f"line {line_no}: duplicate field {key} in {current_id}")
        entries[current_id][key] = value

    if not entries:
        errors.append("no HYP-#### entries found")
        return entries, errors

    for hyp_id, fields in entries.items():
        for field in REQUIRED_FIELDS:
            if not fields.get(field):
                errors.append(f"{hyp_id}: missing field {field}")
        explanation = fields.get("쉬운 설명", "")
        if len(explanation) > 160:
            errors.append(f"{hyp_id}: 쉬운 설명 must be at most 160 characters")
        levels = {part.strip() for part in fields.get("출처 수준", "").split(",") if part.strip()}
        unknown_levels = levels - ALLOWED_LEVELS
        if unknown_levels:
            errors.append(f"{hyp_id}: invalid 출처 수준 {sorted(unknown_levels)}")
        status = fields.get("상태")
        if status and status not in ALLOWED_STATUSES:
            errors.append(f"{hyp_id}: invalid 상태 {status}")
        if status in {"LOCAL_SUPPORTED", "LOCAL_FAILED"} and fields.get("로컬 결과") in {None, "N/A", "PENDING"}:
            errors.append(f"{hyp_id}: {status} requires a local result")
        if status in {"HOSTED_SUPPORTED", "HOSTED_FAILED"} and fields.get("Hosted 결과") in {None, "N/A", "PENDING"}:
            errors.append(f"{hyp_id}: {status} requires a hosted result")
        if status == "PENDING_HOSTED" and not fields.get("Hosted 결과", "").startswith("PENDING"):
            errors.append(f"{hyp_id}: PENDING_HOSTED requires Hosted 결과: PENDING")
    return entries, errors


def validate_card_links(entries: dict[str, dict[str, str]], cards_dir: Path) -> list[str]:
    errors: list[str] = []
    seen_test_ids: dict[str, Path] = {}
    for card in sorted(cards_dir.glob("EXP-*.md")):
        text = card.read_text(encoding="utf-8")
        ids = CARD_ID_RE.findall(text)
        test_ids = CARD_TEST_RE.findall(text)
        if not ids:
            errors.append(f"{card}: missing hypothesis_id: HYP-####")
        if len(ids) > 1:
            errors.append(f"{card}: multiple hypothesis_id fields")
        if not test_ids:
            errors.append(f"{card}: missing test_id: TEST-...")
        if len(test_ids) > 1:
            errors.append(f"{card}: multiple test_id fields")
        for test_id in test_ids:
            if test_id in seen_test_ids:
                errors.append(f"{card}: duplicate {test_id}; already used by {seen_test_ids[test_id]}")
            else:
                seen_test_ids[test_id] = card
        for hyp_id in ids:
            if hyp_id not in entries:
                errors.append(f"{card}: unknown hypothesis id {hyp_id}")
                continue
            if card.name not in entries[hyp_id].get("실험", ""):
                errors.append(f"{card}: {hyp_id} 실험 field does not reference this card")
            has_result = bool(re.search(r"(?m)^## .*결과", text))
            if has_result and entries[hyp_id].get("로컬 결과") in {None, "N/A", "PENDING"}:
                errors.append(f"{card}: result exists but {hyp_id} local result is not updated")
    return errors


def validate_events(entries: dict[str, dict[str, str]], events_dir: Path) -> list[str]:
    errors: list[str] = []
    seen_event_ids: set[str] = set()
    latest_by_hypothesis: dict[str, tuple[Path, dict[str, object]]] = {}
    for event_path in sorted(events_dir.glob("*/*.json")):
        try:
            event = json.loads(event_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{event_path}: invalid JSON: {exc}")
            continue
        required = {
            "schema_version", "event_id", "created_at", "agent", "hypothesis_id",
            "test_id", "reason", "before_entry", "after_entry",
            "ledger_sha256_before", "ledger_sha256_after",
        }
        missing = required - set(event)
        if missing:
            errors.append(f"{event_path}: missing event fields {sorted(missing)}")
            continue
        if event["schema_version"] != 1:
            errors.append(f"{event_path}: schema_version must be 1")
        if event["event_id"] in seen_event_ids:
            errors.append(f"{event_path}: duplicate event_id {event['event_id']}")
        seen_event_ids.add(event["event_id"])
        if event_path.parent.name != event["agent"]:
            errors.append(f"{event_path}: agent does not match parent directory")
        if event["hypothesis_id"] not in entries:
            errors.append(f"{event_path}: unknown hypothesis_id {event['hypothesis_id']}")
        if not re.fullmatch(r"TEST-[A-Z0-9-]+", event["test_id"]):
            errors.append(f"{event_path}: invalid test_id {event['test_id']}")
        after_entry = event["after_entry"]
        if not isinstance(after_entry, dict):
            errors.append(f"{event_path}: after_entry must be an object")
        else:
            for field in REQUIRED_FIELDS:
                if not after_entry.get(field):
                    errors.append(f"{event_path}: after_entry missing {field}")
        for sha_field in ("ledger_sha256_before", "ledger_sha256_after"):
            if not re.fullmatch(r"[0-9a-f]{64}", str(event[sha_field])):
                errors.append(f"{event_path}: invalid {sha_field}")
        hypothesis_id = event["hypothesis_id"]
        previous = latest_by_hypothesis.get(hypothesis_id)
        event_order = (str(event["created_at"]), str(event["event_id"]))
        previous_order = ((str(previous[1]["created_at"]), str(previous[1]["event_id"]))
                          if previous else None)
        if previous_order is None or event_order > previous_order:
            latest_by_hypothesis[hypothesis_id] = (event_path, event)
    for hypothesis_id, (event_path, event) in latest_by_hypothesis.items():
        if entries.get(hypothesis_id) != event["after_entry"]:
            errors.append(f"{event_path}: latest event is not reflected in canonical ledger")
    return errors


def validate_hosted_links(entries: dict[str, dict[str, str]], hosted_text: str) -> list[str]:
    """Check that hosted claims name a submission present in HOSTED_LEDGER."""
    errors: list[str] = []
    known_ids = set(SUBMISSION_ID_RE.findall(hosted_text))
    for hyp_id, fields in entries.items():
        status = fields.get("상태")
        if status not in {"HOSTED_SUPPORTED", "HOSTED_FAILED", "PENDING_HOSTED"}:
            continue
        claimed_ids = set(SUBMISSION_ID_RE.findall(fields.get("Hosted 결과", "")))
        if not claimed_ids:
            errors.append(f"{hyp_id}: hosted status requires submission id in Hosted 결과")
        for submission_id in claimed_ids - known_ids:
            errors.append(f"{hyp_id}: submission {submission_id} missing from hosted ledger")
    for hyp_id in set(re.findall(r"HYP-\d{4}", hosted_text)) - set(entries):
        errors.append(f"hosted ledger references unknown hypothesis id {hyp_id}")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ledger", nargs="?", type=Path, default=ROOT / "HYPOTHESES.md")
    parser.add_argument("--cards-dir", type=Path)
    parser.add_argument("--hosted-ledger", type=Path)
    parser.add_argument("--events-dir", type=Path)
    parser.add_argument("--strict", action="store_true",
                        help="validate the canonical ledger, cards, hosted links, and events")
    args = parser.parse_args()

    if args.strict:
        args.cards_dir = args.cards_dir or ROOT / "experiments" / "cards"
        args.hosted_ledger = args.hosted_ledger or ROOT / "evidence" / "HOSTED_LEDGER.md"
        args.events_dir = args.events_dir or ROOT / "coordination" / "hypotheses"

    try:
        text = args.ledger.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"cannot read ledger: {exc}", file=sys.stderr)
        raise SystemExit(3)

    entries, errors = parse_ledger(text)
    if args.cards_dir:
        errors.extend(validate_card_links(entries, args.cards_dir))
    if args.hosted_ledger:
        try:
            hosted_text = args.hosted_ledger.read_text(encoding="utf-8")
        except OSError as exc:
            errors.append(f"cannot read hosted ledger: {exc}")
        else:
            errors.extend(validate_hosted_links(entries, hosted_text))
    if args.events_dir:
        errors.extend(validate_events(entries, args.events_dir))
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        raise SystemExit(3)
    print(f"hypothesis ledger PASS: {len(entries)} entries")


if __name__ == "__main__":
    main()
