import hashlib
import importlib.util

assert hashlib.sha256(open("main.py", "rb").read()).hexdigest() == "b0c32e1a181e9308c05046b10d618258397c4088e21025ba78346aaa9ac25ddf"
_spec = importlib.util.spec_from_file_location("_v1_timing_early_policy", "main.py")
policy = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(policy)

policy.LAND_PURCHASE_DAYS = (4, 8)
policy.N_HANDS = 4
policy.CARROT_TILES = 15
agent = policy.agent
