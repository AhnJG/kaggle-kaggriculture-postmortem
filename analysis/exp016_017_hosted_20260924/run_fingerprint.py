import subprocess
import sys
import time
import os

NUM_CHUNKS = 8
script_path = 'analysis/exp016_017_hosted_20260924/fingerprint.py'

print(f"Launching {NUM_CHUNKS} parallel fingerprinting workers...")
t0 = time.time()

processes = []
for i in range(NUM_CHUNKS):
    cmd = [
        sys.executable,
        script_path,
        '--chunk-idx', str(i),
        '--num-chunks', str(NUM_CHUNKS)
    ]
    p = subprocess.Popen(cmd)
    processes.append((i, p))

failed = False
for i, p in processes:
    ret = p.wait()
    if ret != 0:
        print(f"Worker {i} failed with return code {ret}")
        failed = True

if failed:
    print("One or more workers failed!")
    sys.exit(1)

t1 = time.time()
print(f"All {NUM_CHUNKS} workers completed in {t1 - t0:.1f} seconds. Merging results...")

# Run merge
merge_cmd = [
    sys.executable,
    script_path,
    '--merge',
    '--num-chunks', str(NUM_CHUNKS)
]
subprocess.run(merge_cmd, check=True)
print("Fingerprinting and merging completed successfully!")
