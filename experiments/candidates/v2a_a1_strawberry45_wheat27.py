import hashlib
import importlib.util
from pathlib import Path

BASE = Path("experiments/candidates/exp003_policy.py")
BASE_SHA256 = "ea02c5ecfe66def23dc0f40303286e2e70bfd594e7047d9bfedb81e9e76c8665"
assert hashlib.sha256(BASE.read_bytes()).hexdigest() == BASE_SHA256

_spec = importlib.util.spec_from_file_location("_v2a_a1_base", BASE)
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)

agent = _base.build_agent(
    crop_counts={"MELON": 3, "STRAWBERRY": 45, "WHEAT": 27},
    sell_mode="B1",
    slot_mode="C1",
)
