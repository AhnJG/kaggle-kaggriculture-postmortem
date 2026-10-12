import subprocess
import os
import glob
import json
import base64
import zlib
import hashlib

slugs = [
    "kaggriculture-more-wheat-smarter-sales",
    "kaggriculture-one-more-wheat",
    "kaggriculture-a-smaller-market-shock",
    "kaggriculture-two-coins-one-sheep-lb-2600",
    "kaggriculture-herd-safe-sale-window-lb-2700",
    "kaggriculture-7-turn-rescue-historical-lb-2800"
]

def extract_from_ipynb(filepath, out_dir):
    with open(filepath, 'r', encoding='utf-8') as f:
        nb = json.load(f)
    
    # Try to find code cells
    script_content = ""
    for cell in nb.get('cells', []):
        if cell.get('cell_type') == 'code':
            source = "".join(cell.get('source', []))
            # Some Kaggle notebooks write to file using %%writefile
            if source.startswith('%%writefile'):
                lines = source.split('\n')
                filename = lines[0].replace('%%writefile', '').strip()
                content = '\n'.join(lines[1:])
                with open(os.path.join(out_dir, filename), 'w', encoding='utf-8') as out_f:
                    out_f.write(content)
            else:
                # It might be a base64 payload
                if 'base64.b64decode' in source and 'zlib.decompress' in source:
                    # try to extract the payload
                    pass # We will do this manually if needed, or parse it
                else:
                    script_content += source + "\n\n"
    return

for slug in slugs:
    print(f"Downloading {slug}...")
    os.makedirs(slug, exist_ok=True)
    subprocess.run(["kaggle", "kernels", "pull", f"dmitriigluzdov/{slug}", "-p", slug], check=True)
