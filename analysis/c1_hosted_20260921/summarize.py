import csv
from collections import defaultdict
import json
import os

out_dir = 'analysis/c1_hosted_20260921'
csv_path = os.path.join(out_dir, 'opponents.csv')

with open(csv_path, 'r') as f:
    reader = csv.DictReader(f)
    results = list(reader)

# Total W/L/D
total_w = sum(1 for r in results if r['result'] == 'W')
total_l = sum(1 for r in results if r['result'] == 'L')
total_d = sum(1 for r in results if r['result'] == 'D')

# Label stats
label_stats = defaultdict(lambda: {'count': 0, 'W': 0, 'L': 0, 'D': 0})
mirror_exact_count = 0

for r in results:
    label = r['label']
    res = r['result']
    label_stats[label]['count'] += 1
    label_stats[label][res] += 1
    if r['MIRROR_EXACT'] == 'True':
        mirror_exact_count += 1

print(f"Total: {len(results)} (W: {total_w}, L: {total_l}, D: {total_d})")
print(f"MIRROR_EXACT: {mirror_exact_count}")
print("\nLabel Stats:")
for label, stats in sorted(label_stats.items(), key=lambda x: x[1]['count'], reverse=True):
    print(f"- {label}: {stats['count']} (W: {stats['W']}, L: {stats['L']}, D: {stats['D']})")
