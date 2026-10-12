import hashlib
import importlib.util

PARENT_SHA256 = "d6cdb83ffdb27d2614330b20d438a6a20e82c7f4a72ead5ca8be897859de0b59"
assert hashlib.sha256(open("main.py", "rb").read()).hexdigest() == PARENT_SHA256
_spec = importlib.util.spec_from_file_location("_v2c_bh1_policy", "main.py")
policy = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(policy)
policy.MELON_TILES = 30
policy.STRAWBERRY_TILES = 0
policy.CROP_SWITCH_DAY = 2
policy.LAND_PURCHASE_HOURS = (0, 0)
agent = policy.agent
