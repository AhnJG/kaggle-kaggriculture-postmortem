import os
import json
import hashlib
from datetime import datetime
import subprocess
from kaggle.api.kaggle_api_extended import KaggleApi

def get_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        h.update(f.read())
    return h.hexdigest()

def main():
    api = KaggleApi()
    api.authenticate()
    
    candidates = {
        'alperen5252525/kaggriculture-before-dawn-stock-cash-sales': 'd49b0540',
        'lynnsakurai/farming-score-v2-a-better-approach': 'f419b98e',
        'tetsutani/market-smart-farming-kaggriculture': 'ac5bfab4',
        'mzcao7/kaggriculture-2476-8-peak-lightgbm-xgboost': '74bd0e7d'
    }
    
    out_dir = "analysis/public_exact_20260919"
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs("docs/collection_snapshots", exist_ok=True)
    
    results_candidates = {}
    changed_count = 0
    
    for ref, expected_hash_prefix in candidates.items():
        user, slug = ref.split('/')
        snap_dir = os.path.join("docs/collection_snapshots", slug)
        os.makedirs(snap_dir, exist_ok=True)
        
        try:
            api.kernels_pull(ref, path=snap_dir, metadata=True)
        except Exception as e:
            results_candidates[ref] = {"error": f"Failed to pull: {e}"}
            continue
            
        files = [f for f in os.listdir(snap_dir) if not f.endswith('.json')]
        if not files:
            results_candidates[ref] = {"error": "no source downloaded"}
            continue
            
        source_file = os.path.join(snap_dir, files[0])
        new_hash = get_sha256(source_file)
        
        status = "SAME"
        if not new_hash.startswith(expected_hash_prefix):
            status = "CHANGED"
            changed_count += 1
            
        meta_file = os.path.join(snap_dir, "kernel-metadata.json")
        meta = {}
        if os.path.exists(meta_file):
            with open(meta_file, 'r') as f:
                meta = json.load(f)
                
        results_candidates[ref] = {
            "status": status,
            "new_sha256": new_hash,
            "version": meta.get('kernel_version', 'N/A') or meta.get('id', 'N/A'),
            "last_run_time": meta.get('last_run_time', 'N/A'),
            "dataset_sources": meta.get('dataset_sources', []),
            "license": meta.get('license', 'N/A')
        }
        
    with open(os.path.join(out_dir, "candidates.json"), 'w') as f:
        json.dump(results_candidates, f, indent=2)
        
    mzcao_ref = 'mzcao7/kaggriculture-2476-8-peak-lightgbm-xgboost'
    ds_sources = results_candidates.get(mzcao_ref, {}).get("dataset_sources", [])
    mzcao_datasets = {}
    
    for ds in ds_sources:
        try:
            res = subprocess.run(["kaggle", "datasets", "files", ds], capture_output=True, text=True, check=True)
            files_out = res.stdout
        except subprocess.CalledProcessError as e:
            files_out = f"Error: {e.stderr}"
            
        try:
            ds_meta = api.dataset_metadata(ds)
            # The KaggleApi usually doesn't return the metadata object directly from dataset_metadata (it downloads it).
            # Instead, we can use dataset_list or just run `kaggle datasets metadata` subprocess if it's easier, but
            # actually we don't need to download metadata. Let's just list with Kaggle API.
            datasets = api.dataset_list(search=ds.split('/')[1])
            ds_info = [d for d in datasets if d.ref == ds]
            if ds_info:
                d = ds_info[0]
                mzcao_datasets[ds] = {
                    "owner": getattr(d, 'ownerName', ds.split('/')[0]),
                    "size": getattr(d, 'size', 'N/A'),
                    "last_update": str(getattr(d, 'lastUpdated', 'N/A')),
                    "license": getattr(d, 'licenseName', 'N/A'),
                    "files": files_out
                }
            else:
                mzcao_datasets[ds] = {"error": "not found in search", "files": files_out}
        except Exception as e:
            mzcao_datasets[ds] = {"error": str(e), "files": files_out}
            
    with open(os.path.join(out_dir, "mzcao7_dataset.json"), 'w') as f:
        json.dump(mzcao_datasets, f, indent=2)
        
    new_nbs = []
    page = 1
    cutoff = datetime(2026, 9, 16)
    
    while True:
        k_list = api.kernels_list(competition="kaggriculture", sort_by="dateRun", page=page)
        if not k_list:
            break
            
        reached_old = False
        for k in k_list:
            if k.last_run_time < cutoff:
                reached_old = True
                continue
                
            snap_dir = os.path.join("docs/collection_snapshots", k.ref.split('/')[1])
            os.makedirs(snap_dir, exist_ok=True)
            
            try:
                api.kernels_pull(k.ref, path=snap_dir, metadata=True)
            except Exception:
                pass
                
            has_submission_gen = False
            score_claim = "N/A"
            ds_deps = False
            
            meta_path = os.path.join(snap_dir, "kernel-metadata.json")
            if os.path.exists(meta_path):
                with open(meta_path, 'r') as mf:
                    km = json.load(mf)
                    ds_deps = len(km.get('dataset_sources', [])) > 0
                    
            files = [f for f in os.listdir(snap_dir) if not f.endswith('.json')]
            for f in files:
                try:
                    with open(os.path.join(snap_dir, f), 'r', errors='ignore') as code_f:
                        content = code_f.read()
                        if "%%writefile main.py" in content or "tar -czf" in content or "tar.gz" in content:
                            has_submission_gen = True
                            
                        import re
                        lines = content.split('\n')
                        for line in lines:
                            if re.search(r'(?i)(?:lb|score|rating).*?(\d{3,4}(?:\.\d+)?)', line):
                                score_claim = line.strip()
                                break
                        if score_claim != "N/A":
                            break
                except Exception:
                    pass
                    
            new_nbs.append({
                "ref": k.ref,
                "title": getattr(k, 'title', 'N/A'),
                "votes": getattr(k, 'totalVotes', 0),
                "last_run": str(k.last_run_time),
                "submission_code_generated": has_submission_gen,
                "external_datasets": ds_deps,
                "score_claim": score_claim
            })
            
        if reached_old:
            break
        page += 1
        
    with open(os.path.join(out_dir, "new_notebooks.json"), 'w') as f:
        json.dump(new_nbs, f, indent=2)
        
    file_hashes = {}
    for f in ["candidates.json", "mzcao7_dataset.json", "new_notebooks.json"]:
        p = os.path.join(out_dir, f)
        if os.path.exists(p):
            file_hashes[f] = get_sha256(p)
            
    with open(os.path.join(out_dir, "file_hashes.json"), 'w') as f:
        json.dump(file_hashes, f, indent=2)

if __name__ == "__main__":
    main()
