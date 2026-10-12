import json
import os
import re
import ast
import zlib
import gzip
import base64
import hashlib
import tarfile
import io
import difflib
from pathlib import Path

OUT_DIR = Path("analysis/lineage_20260919")
EXTRACT_DIR = OUT_DIR / "extracted"
EXTRACT_DIR.mkdir(parents=True, exist_ok=True)

P2_PATH = "releases/public-lynnsakurai-farming-score-v2-exact/submission.tar.gz"

def normalize_code(content):
    if isinstance(content, bytes):
        try:
            content = content.decode('utf-8')
        except UnicodeDecodeError:
            return []
    content = content.replace('\r\n', '\n').replace('\r', '\n')
    lines = content.split('\n')
    norm_lines = []
    for line in lines:
        stripped = line.rstrip()
        if stripped and not stripped.lstrip().startswith('#'):
            norm_lines.append(stripped)
    return norm_lines

def extract_tapes_from_content(content):
    tapes = []
    def is_tape(t):
        if not isinstance(t, list) or len(t) != 719: return False
        if not all(isinstance(x, dict) and 'farmer' in x and 'hands' in x and 'market' in x for x in t): return False
        return True

    def process_data(data):
        if isinstance(data, list):
            if is_tape(data):
                tapes.append(data)
            else:
                for item in data:
                    process_data(item)
        elif isinstance(data, dict):
            if "actions" in data and "routes" in data:
                actions = data["actions"]
                routes = data["routes"]
                if isinstance(routes, dict):
                    for r_id, indices in routes.items():
                        try:
                            t = [actions[i] for i in indices]
                            if is_tape(t): tapes.append(t)
                        except: pass
                elif isinstance(routes, list):
                    for indices in routes:
                        try:
                            t = [actions[i] for i in indices]
                            if is_tape(t): tapes.append(t)
                        except: pass
            else:
                for v in data.values():
                    process_data(v)

    if isinstance(content, str):
        try:
            data = json.loads(content)
            process_data(data)
        except json.JSONDecodeError: pass

        b85_matches = re.findall(r"base64\.b85decode\((['\"])(.*?)\1\)", content)
        b64_matches = re.findall(r"base64\.b64decode\((['\"])(.*?)\1\)", content)
        all_matches = []
        for m in b85_matches:
            try: all_matches.append(base64.b85decode(m[1]))
            except: pass
        for m in b64_matches:
            try: all_matches.append(base64.b64decode(m[1]))
            except: pass
        
        for dec in all_matches:
            try: dec = zlib.decompress(dec)
            except:
                try: dec = gzip.decompress(dec)
                except: pass
            try:
                data = json.loads(dec.decode('utf-8'))
                process_data(data)
            except: pass
    return tapes

def tape_hash(tape):
    return hashlib.sha256(json.dumps(tape[1:], sort_keys=True).encode('utf-8')).hexdigest()

p2_norm_lines = []
base_tape_hashes = set()

with tarfile.open(P2_PATH, "r:gz") as tar:
    for m in tar.getmembers():
        if m.name.endswith(".py"):
            content = tar.extractfile(m).read().decode('utf-8')
            p2_norm_lines.extend(normalize_code(content))
            tapes = extract_tapes_from_content(content)
            for t in tapes:
                base_tape_hashes.add(tape_hash(t))

sorted_base_tape_hashes = sorted(list(base_tape_hashes))
base_hash_str = '\n'.join(sorted_base_tape_hashes)
p2_base_tapes_hash = hashlib.sha256(base_hash_str.encode('utf-8')).hexdigest()
EXPECTED_BASE_HASH = '20f4edeedefab30f30935e96c234d140d9b6ae82339021c635f7fc3fd7466da5'

if len(base_tape_hashes) != 38 or p2_base_tapes_hash != EXPECTED_BASE_HASH:
    print("BLOCKED: Base tape extraction failed!")
    exit(1)

def extract_from_tar(tar_path):
    extracted_files = {}
    try:
        with tarfile.open(tar_path, "r:gz") as tar:
            for m in tar.getmembers():
                if m.isfile():
                    f = tar.extractfile(m)
                    if f:
                        extracted_files[m.name] = f.read()
    except Exception: pass
    return extracted_files

def analyze_candidate(name, files_dict):
    if not files_dict:
        return {"status": "UNKNOWN", "reason": "No files extracted"}
    
    members = list(files_dict.keys())
    main_content = b""
    for k, v in files_dict.items():
        if k.endswith("main.py") or k == "main.py":
            main_content = v
            break
            
    main_sha256 = hashlib.sha256(main_content).hexdigest() if main_content else ""
    
    all_py_lines = []
    py_files = sorted([k for k in files_dict.keys() if k.endswith('.py')])
    for k in py_files:
        all_py_lines.extend(normalize_code(files_dict[k]))
        
    main_lines = len(normalize_code(main_content))
    
    hdr_ozer = False
    if main_content:
        first_80 = main_content.decode('utf-8', errors='ignore').split('\n')[:80]
        for line in first_80:
            if "Ahmed Berat Ozer" in line or "EXP260 combined" in line:
                hdr_ozer = True
                break
                
    mentions = {"yhay81": 0, "thomastschinkel": 0, "aurax7": 0, "tetsutani": 0, "Ozer": 0}
    for k in py_files:
        c = files_dict[k].decode('utf-8', errors='ignore')
        for m in mentions.keys():
            mentions[m] += c.count(m)
            
    sim_method = "SequenceMatcher"
    if len(all_py_lines) > 6000 or len(p2_norm_lines) > 6000:
        sim_method = "quick_ratio"
        sim_p2 = difflib.SequenceMatcher(None, all_py_lines, p2_norm_lines, autojunk=False).quick_ratio()
    else:
        sim_p2 = difflib.SequenceMatcher(None, all_py_lines, p2_norm_lines, autojunk=False).ratio()
        
    tapes_found = 0
    tapes_shared_with_p2 = 0
    unique_tape_hashes = set()
    
    for k, v in files_dict.items():
        try:
            content_str = v.decode('utf-8')
            tapes = extract_tapes_from_content(content_str)
            for t in tapes:
                th = tape_hash(t)
                if th not in unique_tape_hashes:
                    unique_tape_hashes.add(th)
                    tapes_found += 1
                    if th in base_tape_hashes:
                        tapes_shared_with_p2 += 1
        except Exception: pass

    classification = "DIFFERENT"
    if hdr_ozer or sim_p2 >= 0.70 or tapes_shared_with_p2 >= 1:
        classification = "SAME_FAMILY"
    elif 0.30 <= sim_p2 < 0.70:
        classification = "AMBIGUOUS"
    elif sum(mentions[x] for x in ["yhay81", "thomastschinkel", "aurax7"]) >= 1:
        classification = "RELATED"

    return {
        "classification": classification,
        "hdr_ozer": hdr_ozer,
        "mentions": mentions,
        "sim_p2": sim_p2,
        "sim_method": sim_method,
        "tapes_found": tapes_found,
        "tapes_shared_with_p2": tapes_shared_with_p2,
        "main_sha256": main_sha256,
        "main_lines": main_lines,
        "members": members,
        "status": "OK"
    }

def parse_notebook(slug, target_sha):
    nb_path = f"docs/collection_snapshots/{slug}/{slug}.ipynb"
    result = {
        "slug": slug,
        "files_dict": {},
        "status": "UNKNOWN",
        "reason": "",
        "external_dataset": False,
        "score_claim": "N/A"
    }
    if not os.path.exists(nb_path):
        result["reason"] = f"File not found: {nb_path}"
        return result
        
    try:
        with open(nb_path, "r", encoding="utf-8") as f:
            nb = json.load(f)
    except Exception as e:
        result["reason"] = f"JSON parse error: {e}"
        return result

    extracted_files = {}
    external_dataset = False
    
    score_claim = "N/A"
    score_regex = re.compile(r'\b[1-3]\d{3}(\.\d)?\b')
    
    for cell in nb.get("cells", []):
        cell_type = cell.get("cell_type", "")
        source = "".join(cell.get("source", []))
        
        if cell_type == "markdown":
            if score_claim == "N/A":
                sentences = re.split(r'(?<=[.!?])\s+', source)
                for sent in sentences:
                    if score_regex.search(sent):
                        score_claim = sent.strip().replace('\n', ' ')
                        break
                        
        elif cell_type == "code":
            if "/kaggle/input" in source:
                external_dataset = True
                continue
                
            if source.startswith("%%writefile"):
                lines = source.splitlines()
                filename = lines[0].replace("%%writefile", "").strip()
                content = "\n".join(lines[1:]).encode('utf-8')
                extracted_files[filename] = content
                continue
                
            try:
                tree = ast.parse(source)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Assign):
                        for target in node.targets:
                            if isinstance(target, ast.Name) and target.id == "SOURCE_BYTES":
                                val = node.value
                                bytes_concat = b""
                                if isinstance(val, ast.Call) and isinstance(val.func, ast.Attribute) and val.func.attr == "join":
                                    arg = val.args[0]
                                    if hasattr(arg, 'elts'):
                                        for elt in arg.elts:
                                            if isinstance(elt, ast.Constant) and isinstance(elt.value, bytes):
                                                bytes_concat += elt.value
                                elif isinstance(val, ast.Constant) and isinstance(val.value, bytes):
                                    bytes_concat = val.value
                                if bytes_concat:
                                    extracted_files["main.py"] = bytes_concat
                    
                    if isinstance(node, ast.Constant):
                        val = node.value
                        if isinstance(val, str) and len(val) > 100:
                            candidates = [val.encode('utf-8')]
                        elif isinstance(val, bytes) and len(val) > 100:
                            candidates = [val]
                        else:
                            continue
                            
                        for c in candidates:
                            dec_candidates = []
                            try: dec_candidates.append(base64.b85decode(c))
                            except: pass
                            try: dec_candidates.append(base64.b64decode(c))
                            except: pass
                            
                            for dec in dec_candidates:
                                try: dec = zlib.decompress(dec)
                                except:
                                    try: dec = gzip.decompress(dec)
                                    except: pass
                                    
                                try:
                                    with tarfile.open(fileobj=io.BytesIO(dec), mode="r:*") as tar:
                                        for m in tar.getmembers():
                                            if m.isfile():
                                                f = tar.extractfile(m)
                                                if f:
                                                    extracted_files[m.name] = f.read()
                                except Exception:
                                    if dec:
                                        if b"import " in dec or b"def " in dec or b"class " in dec:
                                            extracted_files["main.py"] = dec
                                        else:
                                            pass
            except Exception:
                pass

    if external_dataset:
        result["external_dataset"] = True
        result["reason"] = "extraction_unsupported: external_dataset"
    elif not extracted_files:
        result["reason"] = "extraction_unsupported: no valid patterns found"
    else:
        result["status"] = "OK"
        result["files_dict"] = extracted_files
        
    result["score_claim"] = score_claim
    return result

with open("analysis/public_exact_20260919/new_notebooks.json", "r") as f:
    notebooks = json.load(f)

results = []
different = []
related_ambiguous = []

# 3-1. Controls
controls = [
    {"name": "P2", "path": "releases/public-lynnsakurai-farming-score-v2-exact/submission.tar.gz", "exp_cls": "SAME_FAMILY"},
    {"name": "tetsutani", "path": "releases/public-tetsutani-market-smart-farming-exact/submission.tar.gz", "exp_cls": "SAME_FAMILY"},
    {"name": "alperen", "path": "releases/public-alperen-before-dawn-stock-cash-sales-exact/submission.tar.gz", "exp_cls": "SAME_FAMILY"},
    {"name": "yhay81", "path": "releases/public-yhay81-shop-router-0909-exact/submission.tar.gz", "exp_cls": "SAME_FAMILY"},
    {"name": "boatlee", "path": "opponents/public/boatlee.py", "exp_cls": None},
    {"name": "kaitofukami", "path": "opponents/public/kaitofukami.py", "exp_cls": None},
    {"name": "raykkretzschmar", "path": "opponents/public/raykkretzschmar.py", "exp_cls": None},
]
control_results = []
fail = False
for c in controls:
    if c["path"].endswith(".tar.gz"): files = extract_from_tar(c["path"])
    else:
        try:
            with open(c["path"], "rb") as f: files = {os.path.basename(c["path"]): f.read()}
        except: files = {}
    res = analyze_candidate(c["name"], files)
    res["name"] = c["name"]
    res["expected_classification"] = c["exp_cls"]
    control_results.append(res)
    
for r in control_results:
    if r["expected_classification"] and r["classification"] != r["expected_classification"]: fail = True
    if r["name"] == "P2" and r["sim_p2"] != 1.0: fail = True
    if r["name"] == "tetsutani" and (r["sim_p2"] < 0.85 or r["tapes_shared_with_p2"] != 38): fail = True
    if r["name"] == "alperen" and (r["sim_p2"] < 0.85 or r["tapes_shared_with_p2"] != 38): fail = True
    if r["name"] == "yhay81" and (r["sim_p2"] >= 0.01 or r["tapes_found"] != 13 or r["tapes_shared_with_p2"] != 13): fail = True
    if r["name"] in ["boatlee", "kaitofukami", "raykkretzschmar"] and r.get("sim_p2", 1) >= 0.05: fail = True
if fail: exit(1)
with open(OUT_DIR / "controls.json", "w") as f: json.dump(control_results, f, indent=2)

for nb in notebooks:
    if not nb.get("submission_code_generated", False):
        continue
        
    slug = nb["ref"].split("/")[-1]
    nb_res = parse_notebook(slug, nb.get("submission_sha256", ""))
    
    if nb_res["files_dict"]:
        ext_dir = EXTRACT_DIR / slug
        ext_dir.mkdir(parents=True, exist_ok=True)
        for fname, fcontent in nb_res["files_dict"].items():
            out_file = ext_dir / os.path.basename(fname)
            with open(out_file, "wb") as fw:
                fw.write(fcontent)
                
    ans = analyze_candidate(slug, nb_res["files_dict"])
    
    if nb_res["external_dataset"]:
        ans["classification"] = "UNKNOWN"
        ans["status"] = "UNKNOWN"
        ans["reason"] = "extraction_unsupported: external_dataset"
    elif not nb_res["files_dict"]:
        ans["classification"] = "UNKNOWN"
        ans["status"] = "UNKNOWN"
        ans["reason"] = "extraction_unsupported: no valid patterns found"
        
    out_rec = {
        "slug": slug,
        "ref": nb.get("ref", ""),
        "title": nb.get("title", ""),
        "votes": nb.get("votes", 0),
        "last_run": nb.get("lastRunTime", ""),
        "score_claim": nb_res["score_claim"],
        "classification": ans["classification"],
        "hdr_ozer": ans.get("hdr_ozer", False),
        "mentions": ans.get("mentions", {}),
        "sim_p2": ans.get("sim_p2", 0),
        "sim_method": ans.get("sim_method", ""),
        "tapes_found": ans.get("tapes_found", 0),
        "tapes_shared_with_p2": ans.get("tapes_shared_with_p2", 0),
        "main_sha256": ans.get("main_sha256", ""),
        "main_lines": ans.get("main_lines", 0),
        "members": ans.get("members", []),
        "reason": ans.get("reason", "")
    }
    results.append(out_rec)
    
    if ans["classification"] == "DIFFERENT":
        different.append(out_rec)
    elif ans["classification"] in ["RELATED", "AMBIGUOUS"]:
        related_ambiguous.append(out_rec)

different.sort(key=lambda x: x["sim_p2"])

with open(OUT_DIR / "lineage.json", "w") as f:
    json.dump(results, f, indent=2)

with open(OUT_DIR / "different.json", "w") as f:
    json.dump(different, f, indent=2)
    
with open(OUT_DIR / "related_ambiguous.json", "w") as f:
    json.dump(related_ambiguous, f, indent=2)
    
for nb in notebooks:
    slug = nb["ref"].split("/")[-1]
    nb_res = parse_notebook(slug, nb.get("submission_sha256", ""))
    nb["score_claim"] = nb_res["score_claim"]
    
with open("analysis/public_exact_20260919/new_notebooks.json", "w") as f:
    json.dump(notebooks, f, indent=2)

