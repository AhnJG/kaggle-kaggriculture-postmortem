#!/usr/bin/env python3
"""Record an immutable hypothesis event and update the canonical ledger."""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import os
import re
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

try:
    from validate_hypotheses import REQUIRED_FIELDS, parse_ledger
except ImportError:  # pragma: no cover - package import in tests
    from tools.validate_hypotheses import REQUIRED_FIELDS, parse_ledger


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LEDGER = ROOT / "HYPOTHESES.md"
DEFAULT_EVENTS = ROOT / "coordination" / "hypotheses"
AGENT_RE = re.compile(r"^[a-z][a-z0-9_-]*$")
HYP_RE = re.compile(r"^HYP-\d{4}$")
TEST_RE = re.compile(r"^TEST-[A-Z0-9-]+$")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def render_entry(hypothesis_id: str, fields: dict[str, str]) -> str:
    lines = [f"## {hypothesis_id}"]
    lines.extend(f"- {field}: {fields[field]}" for field in REQUIRED_FIELDS)
    return "\n".join(lines) + "\n"


def replace_entry(text: str, hypothesis_id: str, fields: dict[str, str]) -> str:
    rendered = render_entry(hypothesis_id, fields)
    heading = re.compile(rf"(?m)^## {re.escape(hypothesis_id)}\s*$")
    match = heading.search(text)
    if match is None:
        return text.rstrip() + "\n\n" + rendered
    next_heading = re.search(r"(?m)^## HYP-\d{4}\s*$", text[match.end():])
    end = match.end() + next_heading.start() if next_heading else len(text)
    suffix = text[end:]
    if suffix and not suffix.startswith("\n"):
        suffix = "\n" + suffix
    return text[:match.start()] + rendered.rstrip() + "\n\n" + suffix.lstrip("\n")


def validate_ledger_text(text: str) -> dict[str, dict[str, str]]:
    entries, errors = parse_ledger(text)
    if errors:
        raise ValueError("; ".join(errors))
    return entries


@contextlib.contextmanager
def ledger_lock(events_root: Path, timeout_seconds: float = 10.0):
    events_root.mkdir(parents=True, exist_ok=True)
    lock_path = events_root / ".update.lock"
    deadline = time.monotonic() + timeout_seconds
    while True:
        try:
            descriptor = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
            os.write(descriptor, f"pid={os.getpid()}\n".encode())
            os.close(descriptor)
            break
        except FileExistsError:
            if time.monotonic() >= deadline:
                raise TimeoutError(f"hypothesis ledger lock busy: {lock_path}")
            time.sleep(0.05)
    try:
        yield
    finally:
        lock_path.unlink(missing_ok=True)


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    temporary.write_text(text, encoding="utf-8")
    os.replace(temporary, path)


def recover_latest_events(ledger_path: Path, events_root: Path) -> None:
    """Apply a latest event left behind if a process stopped before ledger replace."""
    text = ledger_path.read_text(encoding="utf-8")
    entries = validate_ledger_text(text)
    latest: dict[str, dict[str, object]] = {}
    events: list[dict[str, object]] = []
    for path in sorted(events_root.glob("*/*.json")):
        events.append(json.loads(path.read_text(encoding="utf-8")))
    for event in sorted(events, key=lambda item: (str(item["created_at"]), str(item["event_id"]))):
        latest[str(event["hypothesis_id"])] = event
    changed = False
    for hypothesis_id, event in latest.items():
        current = entries.get(hypothesis_id)
        after = event["after_entry"]
        if current == after:
            continue
        if current != event["before_entry"]:
            raise ValueError(f"event/ledger conflict for {hypothesis_id}")
        text = replace_entry(text, hypothesis_id, after)  # type: ignore[arg-type]
        entries = validate_ledger_text(text)
        changed = True
    if changed:
        atomic_write(ledger_path, text)


def record_event(
    *,
    ledger_path: Path,
    events_root: Path,
    agent: str,
    hypothesis_id: str | None,
    test_id: str,
    changes: dict[str, str],
    reason: str,
) -> tuple[str, Path]:
    if not AGENT_RE.fullmatch(agent):
        raise ValueError("agent must match [a-z][a-z0-9_-]*")
    if not TEST_RE.fullmatch(test_id):
        raise ValueError("test_id must match TEST-[A-Z0-9-]+")

    with ledger_lock(events_root):
        recover_latest_events(ledger_path, events_root)
        before_text = ledger_path.read_text(encoding="utf-8")
        entries = validate_ledger_text(before_text)
        if hypothesis_id is None:
            highest = max(int(item.split("-")[1]) for item in entries)
            hypothesis_id = f"HYP-{highest + 1:04d}"
            before_entry = None
            after_entry = changes
        else:
            if not HYP_RE.fullmatch(hypothesis_id) or hypothesis_id not in entries:
                raise ValueError(f"unknown hypothesis_id: {hypothesis_id}")
            before_entry = entries[hypothesis_id]
            after_entry = dict(before_entry)
            after_entry.update(changes)

        missing = [field for field in REQUIRED_FIELDS if not after_entry.get(field)]
        if missing:
            raise ValueError(f"missing required fields: {', '.join(missing)}")
        after_text = replace_entry(before_text, hypothesis_id, after_entry)
        validate_ledger_text(after_text)

        created_at = datetime.now(timezone.utc).isoformat(timespec="microseconds")
        event_id = f"EVT-{created_at.replace(':', '').replace('+00:00', 'Z')}-{uuid.uuid4().hex[:8]}"
        event = {
            "schema_version": 1,
            "event_id": event_id,
            "created_at": created_at,
            "agent": agent,
            "hypothesis_id": hypothesis_id,
            "test_id": test_id,
            "reason": reason,
            "before_entry": before_entry,
            "after_entry": after_entry,
            "ledger_sha256_before": sha256_text(before_text),
            "ledger_sha256_after": sha256_text(after_text),
        }
        event_path = events_root / agent / f"{event_id}.json"
        atomic_write(event_path, json.dumps(event, ensure_ascii=False, indent=2) + "\n")
        atomic_write(ledger_path, after_text)
        return hypothesis_id, event_path


def key_value(value: str) -> tuple[str, str]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("expected FIELD=VALUE")
    key, item = value.split("=", 1)
    if key not in REQUIRED_FIELDS or not item.strip():
        raise argparse.ArgumentTypeError("FIELD must be a known non-empty ledger field")
    return key, item.strip()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument("--events-dir", type=Path, default=DEFAULT_EVENTS)
    parser.add_argument("--agent", required=True)
    parser.add_argument("--test-id", required=True)
    parser.add_argument("--reason", required=True)
    parser.add_argument("--hypothesis-id", help="omit to allocate the next HYP-ID")
    parser.add_argument("--set", dest="changes", action="append", type=key_value,
                        required=True, metavar="FIELD=VALUE")
    args = parser.parse_args()

    try:
        hypothesis_id, event_path = record_event(
            ledger_path=args.ledger,
            events_root=args.events_dir,
            agent=args.agent,
            hypothesis_id=args.hypothesis_id,
            test_id=args.test_id,
            changes=dict(args.changes),
            reason=args.reason,
        )
    except (OSError, TimeoutError, ValueError) as exc:
        parser.exit(3, f"hypothesis update failed: {exc}\n")
    print(f"hypothesis update PASS: {hypothesis_id} -> {event_path}")


if __name__ == "__main__":
    main()
