"""
Pre-correction simulation: verify exact counts before touching anything.
Read-only except for printing.
"""
import json, os
from collections import Counter

BASE = r'C:\Users\jenit\OneDrive\Desktop\CircularEconomy'
MANIFEST = os.path.join(BASE, 'datasets', 'material_images', 'dataset_manifest.json')
DATASET_DIR = os.path.join(BASE, 'datasets', 'material_images')
CLASSES = ['Plastic','Aluminum','Copper','Steel','Paper','Glass','Textile','E-waste','Cardboard','Other']
SPLITS  = ['train','val','test']
ALLOWED = {'.jpg','.jpeg','.png','.webp'}

def infer_split_from_path(path):
    p = path.replace('\\\\', '/').replace('\\', '/')
    for part in p.split('/'):
        if part.lower() in ('train','val','test'):
            return part.lower()
    return 'N/A'

with open(MANIFEST) as f:
    m = json.load(f)
entries = m['entries']
print(f"Original entry count: {len(entries)}")

# Deduplicate: keep first occurrence per normalised output_path
seen = set()
deduped = []
removed_dups = 0
for e in entries:
    key = os.path.normcase(os.path.abspath(e.get('output_path','')))
    if key not in seen:
        seen.add(key)
        deduped.append(e)
    else:
        removed_dups += 1
print(f"Removed duplicate entries: {removed_dups}")
print(f"Deduped entry count: {len(deduped)}")

# Count entries with source_split=N/A that will be inferred
na_before = sum(1 for e in deduped if e.get('source_split') == 'N/A')
na_ambiguous = sum(1 for e in deduped if e.get('source_split')=='N/A'
                   and infer_split_from_path(e.get('output_path','')) == 'N/A')
print(f"N/A entries before correction: {na_before}")
print(f"Ambiguous N/A (no train/val/test in path): {na_ambiguous}")

# Apply inferred splits (simulation only)
corrected_entries = []
n_corrected = 0
for e in deduped:
    ec = dict(e)  # shallow copy for simulation
    if ec.get('source_split') == 'N/A':
        inferred = infer_split_from_path(ec.get('output_path',''))
        if inferred != 'N/A':
            ec['source_split'] = inferred
            n_corrected += 1
    corrected_entries.append(ec)
print(f"source_split values corrected: {n_corrected}")

# Simulated manifest counts after correction
mf = {cls: {s: 0 for s in SPLITS} for cls in CLASSES}
for e in corrected_entries:
    cls = e.get('target_class','?')
    sp  = e.get('source_split','?')
    if cls in mf and sp in SPLITS:
        mf[cls][sp] += 1

# Disk counts
disk = {cls: {s: 0 for s in SPLITS} for cls in CLASSES}
for split in SPLITS:
    for cls in CLASSES:
        d = os.path.join(DATASET_DIR, split, cls)
        if os.path.isdir(d):
            disk[cls][split] = len([
                f for f in os.listdir(d)
                if os.path.isfile(os.path.join(d,f))
                and os.path.splitext(f)[1].lower() in ALLOWED
            ])

# Print comparison
hdr = f"{'Class':<12} {'MF-Tr':>7} {'Dsk-Tr':>7} {'MF-Va':>7} {'Dsk-Va':>7} {'MF-Te':>7} {'Dsk-Te':>7} {'Match'}"
print(f"\n{hdr}")
print("-"*70)
all_match = True
for cls in CLASSES:
    match = all(mf[cls][s] == disk[cls][s] for s in SPLITS)
    if not match: all_match = False
    mf_tr=mf[cls]['train']; mf_v=mf[cls]['val']; mf_te=mf[cls]['test']
    dk_tr=disk[cls]['train']; dk_v=disk[cls]['val']; dk_te=disk[cls]['test']
    ok = "OK" if match else "MISMATCH"
    print(f"{cls:<12} {mf_tr:>7} {dk_tr:>7} {mf_v:>7} {dk_v:>7} {mf_te:>7} {dk_te:>7} {ok}")

mf_t  = sum(mf[c][s]   for c in CLASSES for s in SPLITS)
dsk_t = sum(disk[c][s] for c in CLASSES for s in SPLITS)
print(f"{'TOTAL':<12} MF={mf_t}  DISK={dsk_t}  OVERALL={'OK' if all_match else 'MISMATCH'}")
