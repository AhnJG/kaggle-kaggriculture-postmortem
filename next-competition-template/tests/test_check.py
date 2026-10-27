import csv
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import check  # noqa: E402

SHA = "a" * 64


def write(path, header, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


class LedgerTests(unittest.TestCase):
    def test_duplicate_and_gap_are_errors(self):
        rows = [{"exp_id": "EXP-001"}, {"exp_id": "EXP-001"}, {"exp_id": "EXP-004"}]
        errs = check.check_experiments(rows, Path("."))
        self.assertTrue(any("중복" in e for e in errs))
        self.assertTrue(any("EXP-002" in e and "EXP-003" in e for e in errs))

    def test_bad_id_format(self):
        self.assertTrue(check.check_experiments([{"exp_id": "exp1"}], Path(".")))

    def test_non_utc_time_is_error(self):
        errs = check.check_experiments([{"exp_id": "EXP-001", "created_utc": "2026-09-01 21:00 KST"}], Path("."))
        self.assertTrue(any("UTC" in e for e in errs))

    def test_submission_needs_sha(self):
        self.assertTrue(check.check_submissions([{"submission_id": "1", "artifact_sha256": ""}]))
        self.assertFalse(check.check_submissions([{"submission_id": "1", "artifact_sha256": SHA}]))

    def test_template_ledger_passes(self):
        root = Path(__file__).resolve().parent.parent
        self.assertEqual(check.main(["ledger", "--root", str(root)]), 0)


class CalibrationTests(unittest.TestCase):
    def rows(self, pairs):
        return [{"metric": "m", "local_a_minus_b": str(l), "hosted_a": str(ha), "hosted_b": str(hb)}
                for l, ha, hb in pairs]

    def test_agreement_rate(self):
        # 3 agree, 1 disagree (the Kaggriculture EXP-017 pattern: local win, hosted loss)
        s = check.calibration(self.rows([(0.3, 2400, 2200), (-0.1, 1900, 2100), (0.2, 2300, 2100), (0.9, 2100, 2265)]))["m"]
        self.assertEqual((s["agree"], s["n"]), (3, 4))
        self.assertAlmostEqual(s["rate"], 0.75)
        self.assertLess(s["wilson_lower"], s["rate"])

    def test_ties_are_excluded(self):
        s = check.calibration(self.rows([(0, 1, 2), (1, 2, 2), (1, 3, 2)]))["m"]
        self.assertEqual(s["n"], 1)

    def test_gate_exit_codes(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            header = ["pair_id", "metric", "bot_a", "bot_b", "local_a_minus_b", "hosted_a", "hosted_b", "hosted_observed_utc", "note"]
            write(root / "ledger" / "calibration.csv", header,
                  [[i, "m", "a", "b", 1, 2, 1, "", ""] for i in range(4)])
            self.assertEqual(check.main(["calibration", "--root", d, "--threshold", "0.7"]), 0)
            write(root / "ledger" / "calibration.csv", header,
                  [[i, "m", "a", "b", 1, 1 if i % 2 else 2, 2 if i % 2 else 1, "", ""] for i in range(4)])
            self.assertEqual(check.main(["calibration", "--root", d, "--threshold", "0.7"]), 1)
            write(root / "ledger" / "calibration.csv", header, [])
            self.assertEqual(check.main(["calibration", "--root", d]), 1)


if __name__ == "__main__":
    unittest.main()
