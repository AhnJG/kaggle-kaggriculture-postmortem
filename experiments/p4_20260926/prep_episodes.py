import json
import csv
import gzip
import os
import hashlib

def get_sha256(path):
    if not os.path.exists(path): return None
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()

def get_raw_sha256(path):
    if not os.path.exists(path): return None
    # Read raw as bytes (gzipped or not)
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()

# Load CP1/CP2 exclusions
exclude_ids = set()
with open('experiments/search_20260925/tape-holdout-policy.json', 'r') as f:
    policy = json.load(f)
    for cp in policy.get('checkpoints', []):
        exclude_ids.update(cp.get('episodes', []))

print(f"Loaded {len(exclude_ids)} excluded IDs from tape-holdout-policy.json")

episodes = []

# Source A
with open('analysis/step91_id/summary.json', 'r') as f:
    summary_a = json.load(f)

with open('analysis/exp016_017_hosted_20260924/manifest.json', 'r') as f:
    manifest_a = json.load(f)

manifest_map = {m['id']: m for m in manifest_a}

seen_a_eids = set()

for opp_data in summary_a.values():
    opp_path = opp_data['path']
    opp_sha = opp_data['sha']
    for eid_str, ep in opp_data.get('per_episode', {}).items():
        if ep.get('match_full') is True:
            eid = int(eid_str)
            if eid in exclude_ids: continue
            if eid in seen_a_eids: continue
            
            meta = manifest_map.get(eid)
            if not meta: continue
            
            seed = meta['seed']
            if 9000 <= seed <= 9599: continue
            
            seat = meta['seat']
            raw_path = meta['path']
            
            seen_a_eids.add(eid)
            episodes.append({
                'id': eid,
                'source': 'A',
                'seed': seed,
                'seat': seat,
                'raw_path': raw_path,
                'raw_sha256': meta['sha256'],
                'opp_path': opp_path,
                'opp_sha256': opp_sha
            })

# Source B
with open('analysis/dp_hosted_20260924/file_hashes.json', 'r') as f:
    hashes_b = json.load(f)

name_to_path = {v['name']: v['path'] for k, v in hashes_b.items()}
name_to_sha = {v['name']: k for k, v in hashes_b.items()}

with open('analysis/dp_hosted_20260924/opponents.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row.get('match_full') == 'True':
            eid = int(row['episode'])
            if eid in exclude_ids: continue
            
            seed = int(row['seed'])
            if 9000 <= seed <= 9599: continue
            
            sub = row['submission']
            if sub == '56502662': continue
            
            seat = int(row['dp_seat'])
            opp_name = row['closest_file']
            opp_path = name_to_path.get(opp_name)
            if not opp_path: continue
            
            raw_path = f"private_artifacts/dp_hosted_20260924/raw/{eid}.json.gz"
            if not os.path.exists(raw_path):
                # Try without .gz
                raw_path = f"private_artifacts/dp_hosted_20260924/raw/{eid}.json"
                if not os.path.exists(raw_path):
                    continue
            
            source = 'B_panel47' if 'panel47' in opp_name else 'B'
            
            episodes.append({
                'id': eid,
                'source': source,
                'seed': seed,
                'seat': seat,
                'raw_path': raw_path,
                'raw_sha256': get_raw_sha256(raw_path),
                'opp_path': opp_path,
                'opp_sha256': name_to_sha.get(opp_name)
            })

# Additional checks (720 steps, default config) will be done when loading the raw JSONs.
# To save time, we will write episodes.json now.
with open('experiments/p4_20260926/episodes.json', 'w') as f:
    json.dump(episodes, f, indent=2)

print(f"Found {len([e for e in episodes if e['source'] == 'A'])} Source A episodes.")
print(f"Found {len([e for e in episodes if e['source'].startswith('B')])} Source B episodes.")
print(f"Total: {len(episodes)}")
