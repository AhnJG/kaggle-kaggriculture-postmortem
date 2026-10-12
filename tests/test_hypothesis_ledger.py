#!/usr/bin/env python3
"""Tests for the hypothesis-ledger schema and card links."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tools.validate_hypotheses import (
    parse_ledger,
    validate_card_links,
    validate_events,
    validate_hosted_links,
)
from tools.update_hypotheses import record_event, recover_latest_events, replace_entry


VALID_ENTRY = """# Hypotheses
schema_version: 1

## HYP-0001
- 쉬운 설명: 최신 계획이 이전 계획보다 더 많은 돈을 버는지 확인한다.
- 주장: candidate가 parent보다 강하다.
- 출처 수준: HYPOTHESIS,LOCAL
- 출처: experiments/cards/EXP-001-example.md
- 엔진: 1.32.7
- 실험: experiments/cards/EXP-001-example.md
- 로컬 결과: paired 20 games PASS
- Hosted 결과: N/A
- 상태: LOCAL_SUPPORTED
- 유효 범위: 고정 seed와 두 좌석에서만 확인
- 다음 행동: hosted 검증 전에는 승격 주장 금지
"""


class HypothesisLedgerTests(unittest.TestCase):
    def test_valid_entry(self):
        entries, errors = parse_ledger(VALID_ENTRY)
        self.assertEqual(errors, [])
        self.assertIn("HYP-0001", entries)

    def test_missing_easy_explanation_fails(self):
        text = VALID_ENTRY.replace("- 쉬운 설명: 최신 계획이 이전 계획보다 더 많은 돈을 버는지 확인한다.\n", "")
        _, errors = parse_ledger(text)
        self.assertIn("HYP-0001: missing field 쉬운 설명", errors)

    def test_duplicate_id_fails(self):
        _, errors = parse_ledger(VALID_ENTRY + VALID_ENTRY.split("## HYP-0001", 1)[1].join(["\n## HYP-0001", ""]))
        self.assertTrue(any("duplicate id HYP-0001" in error for error in errors))

    def test_pending_hosted_requires_pending_value(self):
        text = VALID_ENTRY.replace("- 상태: LOCAL_SUPPORTED", "- 상태: PENDING_HOSTED")
        _, errors = parse_ledger(text)
        self.assertIn("HYP-0001: PENDING_HOSTED requires Hosted 결과: PENDING", errors)

    def test_card_requires_known_hypothesis_id(self):
        entries, errors = parse_ledger(VALID_ENTRY)
        self.assertEqual(errors, [])
        with tempfile.TemporaryDirectory() as tmp:
            cards = Path(tmp)
            card = cards / "EXP-001-example.md"
            card.write_text("hypothesis_id: HYP-0001\ntest_id: TEST-0001\n", encoding="utf-8")
            self.assertEqual(validate_card_links(entries, cards), [])
            card.write_text("hypothesis_id: HYP-9999\ntest_id: TEST-0001\n", encoding="utf-8")
            self.assertTrue(any("unknown hypothesis id" in error
                                for error in validate_card_links(entries, cards)))

    def test_card_result_requires_ledger_update(self):
        entries, errors = parse_ledger(VALID_ENTRY.replace(
            "- 로컬 결과: paired 20 games PASS", "- 로컬 결과: N/A").replace(
            "- 상태: LOCAL_SUPPORTED", "- 상태: PLANNED"))
        self.assertEqual(errors, [])
        with tempfile.TemporaryDirectory() as tmp:
            cards = Path(tmp)
            (cards / "EXP-001-example.md").write_text(
                "hypothesis_id: HYP-0001\ntest_id: TEST-0001\n\n## 결과 — PASS\n",
                encoding="utf-8")
            self.assertTrue(any("local result is not updated" in error
                                for error in validate_card_links(entries, cards)))

    def test_hosted_status_requires_known_submission(self):
        text = VALID_ENTRY.replace("- 상태: LOCAL_SUPPORTED", "- 상태: HOSTED_SUPPORTED").replace(
            "- Hosted 결과: N/A", "- Hosted 결과: submission 56165718 PASS")
        entries, errors = parse_ledger(text)
        self.assertEqual(errors, [])
        self.assertEqual(validate_hosted_links(entries, "submission 56165718"), [])
        self.assertTrue(any("missing from hosted ledger" in error
                            for error in validate_hosted_links(entries, "submission 56068891")))

    def test_duplicate_test_id_fails(self):
        entries, _ = parse_ledger(VALID_ENTRY)
        with tempfile.TemporaryDirectory() as tmp:
            cards = Path(tmp)
            for number in (1, 2):
                (cards / f"EXP-00{number}-example.md").write_text(
                    "hypothesis_id: HYP-0001\ntest_id: TEST-0001\n", encoding="utf-8")
            self.assertTrue(any("duplicate TEST-0001" in error
                                for error in validate_card_links(entries, cards)))

    def test_record_event_updates_ledger_and_writes_audit_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ledger = root / "HYPOTHESES.md"
            events = root / "events"
            ledger.write_text(VALID_ENTRY, encoding="utf-8")
            hypothesis_id, event_path = record_event(
                ledger_path=ledger,
                events_root=events,
                agent="codex",
                hypothesis_id="HYP-0001",
                test_id="TEST-0001",
                changes={"상태": "INCONCLUSIVE", "다음 행동": "표본을 고정해 다시 시험"},
                reason="test update",
            )
            self.assertEqual(hypothesis_id, "HYP-0001")
            entries, errors = parse_ledger(ledger.read_text(encoding="utf-8"))
            self.assertEqual(errors, [])
            self.assertEqual(entries[hypothesis_id]["상태"], "INCONCLUSIVE")
            self.assertTrue(event_path.exists())
            self.assertEqual(validate_events(entries, events), [])

    def test_record_event_allocates_next_hypothesis_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ledger = root / "HYPOTHESES.md"
            ledger.write_text(VALID_ENTRY, encoding="utf-8")
            source_entry = parse_ledger(VALID_ENTRY)[0]["HYP-0001"]
            hypothesis_id, _ = record_event(
                ledger_path=ledger,
                events_root=root / "events",
                agent="claude",
                hypothesis_id=None,
                test_id="TEST-0002",
                changes={**source_entry, "쉬운 설명": "두 번째 가설을 쉽게 설명한다."},
                reason="new hypothesis",
            )
            self.assertEqual(hypothesis_id, "HYP-0002")
            entries, errors = parse_ledger(ledger.read_text(encoding="utf-8"))
            self.assertEqual(errors, [])
            self.assertIn("HYP-0002", entries)

    def test_cross_agent_latest_event_uses_time_not_directory_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ledger = root / "HYPOTHESES.md"
            events = root / "events"
            ledger.write_text(VALID_ENTRY, encoding="utf-8")
            record_event(
                ledger_path=ledger, events_root=events, agent="codex",
                hypothesis_id="HYP-0001", test_id="TEST-0001",
                changes={"다음 행동": "Codex update"}, reason="first",
            )
            _, claude_event_path = record_event(
                ledger_path=ledger, events_root=events, agent="claude",
                hypothesis_id="HYP-0001", test_id="TEST-0001",
                changes={"다음 행동": "Claude update"}, reason="second",
            )
            entries, _ = parse_ledger(ledger.read_text(encoding="utf-8"))
            self.assertEqual(validate_events(entries, events), [])

            claude_event = json.loads(claude_event_path.read_text(encoding="utf-8"))
            stale_text = replace_entry(
                ledger.read_text(encoding="utf-8"), "HYP-0001", claude_event["before_entry"])
            ledger.write_text(stale_text, encoding="utf-8")
            recover_latest_events(ledger, events)
            recovered, _ = parse_ledger(ledger.read_text(encoding="utf-8"))
            self.assertEqual(recovered["HYP-0001"]["다음 행동"], "Claude update")


if __name__ == "__main__":
    unittest.main()
