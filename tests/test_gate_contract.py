#!/usr/bin/env python3
"""WP3 machine gate contract tests (stdlib only)."""

from __future__ import annotations

import unittest
import json
import subprocess
import sys
from pathlib import Path

from tools.gate_contract import document, exit_code, validate
from tools.instrument import Counters

ROOT = Path(__file__).resolve().parents[1]


class GateContractTests(unittest.TestCase):
    def test_exit_contract(self):
        self.assertEqual(exit_code("PASS"), 0)
        self.assertEqual(exit_code("FAILURE"), 2)
        self.assertEqual(exit_code("INCONCLUSIVE"), 2)
        self.assertEqual(exit_code("INVALID"), 3)
        self.assertEqual(exit_code("ENGINE_MISMATCH"), 4)
        self.assertEqual(exit_code("IDENTITY_MISMATCH"), 4)

    def test_versioned_document_is_valid(self):
        result = document(verdict="PASS", gate_passed=True, reasons=[],
                          engine_sha256="a" * 64, artifact_sha256={}, payload=[])
        self.assertEqual(validate(result), [])

    def test_missing_required_field_fails_schema(self):
        result = document(verdict="FAILURE", gate_passed=False, reasons=["x"],
                          engine_sha256="a" * 64, artifact_sha256={}, payload=[])
        del result["schema_version"]
        self.assertIn("missing field: schema_version", validate(result))

    def test_non_boolean_gate_flag_fails_schema(self):
        result = document(verdict="PASS", gate_passed=True, reasons=[],
                          engine_sha256="a" * 64, artifact_sha256={}, payload=[])
        result["gate_passed"] = "true"
        self.assertIn("gate_passed must be boolean", validate(result))

    def test_invalid_verdict_and_sha_fail_schema(self):
        result = document(verdict="BOGUS", gate_passed=False, reasons=[1],
                          engine_sha256="bad", artifact_sha256={}, payload=[])
        errors = validate(result)
        self.assertIn("verdict is not an allowed value", errors)
        self.assertIn("reasons entries must be strings", errors)
        self.assertIn("engine_sha256 contains an invalid SHA-256", errors)

    def test_smoke_wrong_step_count_is_invalid(self):
        out = Path("/tmp/wp3-smoke-test.json")
        result = subprocess.run(
            [sys.executable, str(ROOT / "tools/smoke.py"), "--outdir", "",
             "--steps", "1", "--require-pass", "--json", str(out)],
            cwd=ROOT, capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
        self.assertEqual(validate(json.loads(out.read_text())), [])

    def test_smoke_pass_fixture_is_zero(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "tools/smoke.py"), "--outdir", "",
             "--require-pass"], cwd=ROOT, capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_arena_wrong_step_count_is_invalid(self):
        out = Path("/tmp/wp3-arena-test.json")
        result = subprocess.run(
            [sys.executable, str(ROOT / "tools/arena.py"), "--a", "pass",
             "--b", "starter", "--seeds", "1", "--steps", "1",
             "--require-pass", "--json", str(out)],
            cwd=ROOT, capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
        self.assertEqual(json.loads(out.read_text())["verdict"], "INVALID")

    def test_arena_non_done_fixture_is_invalid(self):
        from tools import arena
        original_play = arena.play
        try:
            arena.play = lambda *args, **kwargs: (0, 0, ["ACTIVE", "DONE"], 720)
            result = arena.run("a", "b", [1], verbose=False)
        finally:
            arena.play = original_play
        self.assertEqual(result["errors"], 2)

    def test_validate_gate_cli_rejects_bad_schema(self):
        out = Path("/tmp/wp3-invalid-schema.json")
        out.write_text(json.dumps({"schema_version": 1}), encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(ROOT / "tools/validate_gate.py"), str(out)],
            cwd=ROOT, capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 3, result.stdout + result.stderr)

    def test_engine_mismatch_is_exit_four(self):
        from tools.arena import verdict_kind
        result = {"engine_sha256": "0" * 64, "errors": 0,
                  "ci95": [1.0, 1.0]}
        self.assertEqual(verdict_kind(result), "ENGINE_MISMATCH")
        self.assertEqual(exit_code(verdict_kind(result)), 4)

    def test_diagnostic_mode_keeps_zero_exit(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "tools/arena.py"), "--a", "pass",
             "--b", "starter", "--seeds", "1", "--steps", "1"],
            cwd=ROOT, capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_instrument_silent_failure_is_failure(self):
        fixture = ROOT / "tests/fixtures/silent_failure_agent.py"
        out = Path("/tmp/wp3-instrument-test.json")
        result = subprocess.run(
            [sys.executable, str(ROOT / "tools/instrument.py"), "--a", str(fixture),
             "--b", str(fixture), "--seeds", "7", "--require-pass",
             "--json", str(out)],
            cwd=ROOT, capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        doc = json.loads(out.read_text())
        self.assertEqual(doc["verdict"], "FAILURE")
        self.assertEqual(doc["metric_schema_version"], 3)
        self.assertTrue(any(doc["player_gate_reasons"].values()))

    def test_sentinel_sell_overrequest_is_diagnostic_only(self):
        fixture = ROOT / "tests/fixtures/sentinel_sell_agent.py"
        out = Path("/tmp/gate-split-sentinel-sell.json")
        result = subprocess.run(
            [sys.executable, str(ROOT / "tools/instrument.py"), "--a", str(fixture),
             "--b", str(fixture), "--seeds", "7", "--require-pass",
             "--json", str(out)],
            cwd=ROOT, capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        doc = json.loads(out.read_text())
        for player in doc["payload"][0]["players"]:
            self.assertGreater(player["sell_unfilled"], 0)
            self.assertEqual(player["shed_unsold"], 0)
            self.assertTrue(player["gate_passed"])
            self.assertTrue(player["gate_diagnostics"])

    def test_real_loss_still_fails_release_gate(self):
        self.assertFalse(Counters(shed_discarded=1).is_clean())
        self.assertFalse(Counters(hire_failed=1).is_clean())
        self.assertFalse(Counters(shed_unsold=1).is_clean())

    def test_hire_failure_run_fails_release_gate(self):
        fixture = ROOT / "tests/fixtures/hire_failure_agent.py"
        out = Path("/tmp/gate-split-hire-failure.json")
        result = subprocess.run(
            [sys.executable, str(ROOT / "tools/instrument.py"), "--a", str(fixture),
             "--b", str(fixture), "--seeds", "7", "--require-pass",
             "--json", str(out)],
            cwd=ROOT, capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        doc = json.loads(out.read_text())
        for player in doc["payload"][0]["players"]:
            self.assertGreater(player["hire_failed"], 0)
            self.assertFalse(player["gate_passed"])
            self.assertTrue(any(reason.startswith("hire_failed=")
                                for reason in player["gate_reasons"]))

    def test_instrument_gates_only_selected_player_but_keeps_both_measurements(self):
        clean = ROOT / "tests/fixtures/sentinel_sell_agent.py"
        dirty = ROOT / "tests/fixtures/silent_failure_agent.py"
        out = Path("/tmp/p1b-parent-only-gate.json")
        result = subprocess.run(
            [sys.executable, str(ROOT / "tools/instrument.py"), "--a", str(clean),
             "--b", str(dirty), "--seeds", "7", "--gate-agent", "a",
             "--time-agent", "both", "--require-pass", "--json", str(out)],
            cwd=ROOT, capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        doc = json.loads(out.read_text())
        self.assertEqual(doc["verdict"], "PASS")
        self.assertEqual(doc["gated_player_indices"], [0])
        self.assertEqual(doc["gate_verdict_by_player"]["7"], [True, False])
        self.assertEqual(len(doc["payload"][0]["players"]), 2)
        self.assertEqual(len(doc["payload"][0]["agent_ms_by_player"]), 2)
        self.assertIsNotNone(doc["payload"][0]["combined_agent_cpu_seconds"])
        self.assertTrue(doc["player_gate_reasons"]["7"][1])

    def test_hands_length_mismatch_fails_selected_player(self):
        self.assertFalse(Counters(hands_length_mismatch_count=1).is_clean())
        self.assertIn(
            "hands_length_mismatch_count=1",
            Counters(hands_length_mismatch_count=1).gate_reasons(),
        )


if __name__ == "__main__":
    unittest.main()
