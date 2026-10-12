import ast
import hashlib
import itertools
import json
import math
import re
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PARENT = ROOT / "releases/mirror-screen-v171/main.py"


def mutation_specs(source):
    tree = ast.parse(source)
    constants = {}
    aliases = {}
    defs = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
    for n in tree.body:
        if not isinstance(n, ast.Assign) or len(n.targets) != 1 or not isinstance(n.targets[0], ast.Name):
            continue
        name = n.targets[0].id
        if isinstance(n.value, ast.Name) and name.endswith("_PARENT"):
            aliases[name] = n.value.id
        if not re.fullmatch(r"_?[A-Z][A-Z0-9_]{2,}", name):
            continue
        try:
            value = ast.literal_eval(n.value)
        except (ValueError, TypeError):
            continue
        if type(value) in (int, float) and math.isfinite(value):
            constants[name] = value
    excluded = re.compile(
        r"GOOSE|COOP|EGG|QUAD|LAND|ADV_LOOK|ADVANCE|LEAD|STARTER|PPO|CLEAN|WEED|TURNS_PER_DAY|LAST_STEP|MAX_ORDERS|SHED_CAP"
    )
    specs = []
    for name, value in constants.items():
        if excluded.search(name):
            continue
        step = 1 if type(value) == int else abs(value) * 0.1 if value else 0.1
        for sign in (-1, 1):
            specs.append(dict(kind="constant", target=name, old=value, new=value + sign * step))
    for outer, fn in aliases.items():
        if fn not in defs:
            continue
        calls = {
            n.func.id
            for n in ast.walk(defs[fn])
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id.endswith("_PARENT")
        }
        if len(calls) == 1:
            inner = next(iter(calls))
            if inner in aliases and inner != outer:
                specs.append(dict(kind="layer", target=outer, old=fn, new=inner))
    return specs


src = PARENT.read_bytes()
specs = mutation_specs(src)
constants = [x for x in specs if x["kind"] == "constant"]
layers = [x for x in specs if x["kind"] == "layer"]
ordered = []
for pair in itertools.zip_longest(constants, layers):
    ordered.extend(x for x in pair if x)

dp_h = [x for x in ordered if x["target"] == "_DP_H"]
assert dp_h == [
    {"kind": "constant", "target": "_DP_H", "old": 9, "new": 8},
    {"kind": "constant", "target": "_DP_H", "old": 9, "new": 10},
]

variants_dir = HERE / "variants"
variants_dir.mkdir(exist_ok=True)
out = []
for i, change in enumerate(ordered):
    text = "\n# Frozen search wrapper; parent bytes above are unchanged.\n_SEARCH_ENTRY = [v for v in globals().values() if callable(v)][-1]\n"
    text += change["target"] + " = " + (repr(change["new"]) if change["kind"] == "constant" else change["new"]) + "\n"
    text += "def search_entry(obs, configuration=None):\n    return _SEARCH_ENTRY(obs, configuration)\n"
    content = src + text.encode()
    vid = f"v{i:03}"
    path = variants_dir / f"{vid}.py"
    path.write_bytes(content)
    compile(content, str(path), "exec")
    out.append(
        {
            "id": vid,
            "path": str(path.relative_to(ROOT)),
            "sha256": hashlib.sha256(content).hexdigest(),
            "change": change,
        }
    )

variants_path = HERE / "variants.json"
variants_path.write_text(json.dumps(out, indent=1) + "\n")
print(json.dumps({
    "variants": len(out),
    "constants": len(constants),
    "layers": len(layers),
    "parent_sha256": hashlib.sha256(src).hexdigest(),
    "variants_sha256": hashlib.sha256(variants_path.read_bytes()).hexdigest(),
}))
