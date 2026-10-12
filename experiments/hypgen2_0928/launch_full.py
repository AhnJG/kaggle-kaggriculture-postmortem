"""Fail closed before dispatching any post-smoke job. Never uploads or submits."""
import json
import sys
from pathlib import Path

OUT=Path(__file__).resolve().parent
status=json.loads((OUT/'smoke-summary.json').read_text())
if status['verdict']!='PASS' or not status['full_execution_enabled']:
    raise SystemExit('STOP: frozen smoke gate FAIL; full panel and D3 jobs must not run.')
raise SystemExit('Smoke passed. Independent review and isolated D3 process launcher are required before cloud execution; no implicit dispatch.')
