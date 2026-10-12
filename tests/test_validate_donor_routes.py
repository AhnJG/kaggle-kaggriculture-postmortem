"""Frozen raw-sample integration test; requires private replay artifacts."""
import json
from pathlib import Path
import subprocess
import tempfile
import unittest


class ValidatorTests(unittest.TestCase):
    def test_altered_cash_fails_with_nonzero_exit(self):
        data = json.loads(Path('experiments/results/top10_donor_routes_20260916/analysis.json').read_text())
        data['donors']['Majkel1337']['divergence_contexts']['25'][0]['cash'] = 999
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp)/'analysis.json'; output = Path(tmp)/'validation.json'
            source.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n')
            result = subprocess.run(['python3', 'tools/validate_donor_routes.py', '--analysis', str(source),
                                     '--output', str(output)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1, result.stderr)
            checks = json.loads(output.read_text())['checks']
            self.assertTrue(any(c['name']=='Majkel1337_alignment' and c['result']=='FAIL' for c in checks))


if __name__ == '__main__':
    unittest.main()
