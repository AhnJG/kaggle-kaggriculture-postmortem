import os
import json
import base64
import glob
import re
import hashlib

def process_notebook(filepath):
    print(f"Processing {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        nb = json.load(f)
    
    out_dir = os.path.dirname(filepath)
    has_payload = False
    for cell in nb.get('cells', []):
        if cell.get('cell_type') == 'code':
            source = "".join(cell.get('source', []))
            
            # Pattern 1: %%writefile main.py
            if source.startswith('%%writefile'):
                lines = source.split('\n')
                filename = lines[0].replace('%%writefile', '').strip()
                content = '\n'.join(lines[1:])
                with open(os.path.join(out_dir, filename), 'w', encoding='utf-8') as out_f:
                    out_f.write(content)
                print(f"  Extracted {filename} via %%writefile")
                
            # Pattern 2: ARCHIVE_BYTES or EXPECTED_SUBMISSION_SHA256
            match = re.search(r"ARCHIVE_BYTES\s*=\s*base64\.b64decode\(\s*(?:b)?['\"]([a-zA-Z0-9+/=]+)['\"]", source)
            if match:
                payload = match.group(1)
                try:
                    decoded = base64.b64decode(payload)
                    with open(os.path.join(out_dir, "submission.tar.gz"), 'wb') as out_f:
                        out_f.write(decoded)
                    print("  Extracted submission.tar.gz")
                    os.system(f"cd {out_dir} && tar -xzf submission.tar.gz")
                except Exception as e:
                    print("  Failed to decode:", e)

            sha_match = re.search(r"EXPECTED_SUBMISSION_SHA256\s*=\s*['\"](.*?)['\"]", source)
            if sha_match:
                print(f"  Found EXPECTED_SUBMISSION_SHA256: {sha_match.group(1)}")

for f in glob.glob("*/*.ipynb"):
    process_notebook(f)
