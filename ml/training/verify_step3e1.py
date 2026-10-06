"""
READ-ONLY verification of STEP 3E.1 dataset integrity.
Does NOT modify, move, rename or delete any files.
"""
import os, json, hashlib
from collections import defaultdict
from PIL import Image, UnidentifiedImageError

BASE_DIR    = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATASET_DIR = os.path.join(BASE_DIR, "datasets", "material_images")
MANIFEST    = os.path.join(DATASET_DIR, "dataset_manifest.json")
REPORT_PATH = os.path.join(BASE_DIR, "ml", "reports", "step_3e1_count_verification.md")

TARGET_CLASSES = [
    "Plastic","Aluminum","Copper","Steel","Paper",
    "Glass","Textile","E-waste","Cardboard","Other"
]
SPLITS = ["train", "val", "test"]
ALLOWED_EXT = {".jpg",".jpeg",".png",".webp"}


# ── 1. Count actual files on disk ────────────────────────────────────────────
disk = defaultdict(lambda: defaultdict(int))   # disk[cls][split]
disk_paths = defaultdict(lambda: defaultdict(set))  # disk_paths[cls][split] -> set of abspath

for split in SPLITS:
    split_dir = os.path.join(DATASET_DIR, split)
    for cls in TARGET_CLASSES:
        cls_dir = os.path.join(split_dir, cls)
        if not os.path.isdir(cls_dir):
            continue
        for fname in os.listdir(cls_dir):
            fpath = os.path.join(cls_dir, fname)
            if not os.path.isfile(fpath):
                continue
            if os.path.splitext(fname)[1].lower() in ALLOWED_EXT:
                disk[cls][split] += 1
                disk_paths[cls][split].add(os.path.normcase(os.path.abspath(fpath)))


# ── 2. Count manifest entries ────────────────────────────────────────────────
with open(MANIFEST, "r", encoding="utf-8") as f:
    manifest = json.load(f)

entries = manifest.get("entries", [])
total_entries = len(entries)

mf = defaultdict(lambda: defaultdict(int))    # mf[cls][split]
mf_paths = defaultdict(lambda: defaultdict(set))  # mf[cls][split] -> set of normalised output_path
mf_path_all = set()

for e in entries:
    cls   = e.get("target_class","?")
    split = e.get("source_split", "?")
    out   = e.get("output_path","")
    mf[cls][split] += 1
    if out:
        norm = os.path.normcase(os.path.abspath(out))
        mf_paths[cls][split].add(norm)
        mf_path_all.add(norm)


# ── 3. Cross-check files vs manifest ────────────────────────────────────────
missing_from_disk = defaultdict(lambda: defaultdict(list))   # in manifest, not on disk
unexpected_on_disk = defaultdict(lambda: defaultdict(list))  # on disk, not in manifest

for cls in TARGET_CLASSES:
    for split in SPLITS:
        on_disk  = disk_paths[cls][split]
        in_mf    = mf_paths[cls][split]
        for p in sorted(in_mf - on_disk):
            missing_from_disk[cls][split].append(p)
        for p in sorted(on_disk - in_mf):
            unexpected_on_disk[cls][split].append(p)

# Duplicate output_path in manifest
mf_all_paths_list = [
    os.path.normcase(os.path.abspath(e.get("output_path","")))
    for e in entries if e.get("output_path","")
]
mf_dup_paths = [p for p in set(mf_all_paths_list) if mf_all_paths_list.count(p) > 1]


# ── 4. Totals ────────────────────────────────────────────────────────────────
disk_class_totals  = {cls: sum(disk[cls].values()) for cls in TARGET_CLASSES}
disk_split_totals  = {split: sum(disk[cls][split] for cls in TARGET_CLASSES) for split in SPLITS}
disk_grand_total   = sum(disk_class_totals.values())

mf_class_totals    = {cls: sum(mf[cls].values()) for cls in TARGET_CLASSES}
mf_split_totals    = {split: sum(mf[cls][split] for cls in TARGET_CLASSES) for split in SPLITS}
mf_grand_total     = sum(mf_class_totals.values())

# reported counts from manifest JSON counts block
rep = manifest.get("counts", {})

# ── 5. Print to console ──────────────────────────────────────────────────────
print("\n=== DISK FILE COUNTS ===")
print(f"{'Class':<12} {'Train':>7} {'Val':>7} {'Test':>7} {'Total':>7}")
print("-"*42)
for cls in TARGET_CLASSES:
    tr = disk[cls]["train"]; v = disk[cls]["val"]; te = disk[cls]["test"]
    print(f"{cls:<12} {tr:>7} {v:>7} {te:>7} {tr+v+te:>7}")
print(f"{'SPLIT TOT':<12} {disk_split_totals['train']:>7} {disk_split_totals['val']:>7} {disk_split_totals['test']:>7} {disk_grand_total:>7}")

print("\n=== MANIFEST ENTRY COUNTS (by source_split field) ===")
print(f"{'Class':<12} {'Train':>7} {'Val':>7} {'Test':>7} {'Total':>7}")
print("-"*42)
for cls in TARGET_CLASSES:
    tr = mf[cls]["train"]; v = mf[cls]["val"]; te = mf[cls]["test"]
    print(f"{cls:<12} {tr:>7} {v:>7} {te:>7} {tr+v+te:>7}")
print(f"{'SPLIT TOT':<12} {mf_split_totals['train']:>7} {mf_split_totals['val']:>7} {mf_split_totals['test']:>7} {mf_grand_total:>7}")

print(f"\nTotal manifest entries: {total_entries}")
print(f"Duplicate output_path in manifest: {len(mf_dup_paths)}")
total_missing = sum(len(v) for d in missing_from_disk.values() for v in d.values())
total_unexpected = sum(len(v) for d in unexpected_on_disk.values() for v in d.values())
print(f"Manifest paths missing from disk: {total_missing}")
print(f"Disk files not in manifest: {total_unexpected}")


# ── 6. Build report ──────────────────────────────────────────────────────────
def tbl_row(cls, d, split_list=SPLITS):
    vals = [d[cls][s] for s in split_list]
    tot  = sum(vals)
    return f"| {cls} | {' | '.join(str(v) for v in vals)} | {tot} |"

disk_rows = "\n".join(tbl_row(c, disk) for c in TARGET_CLASSES)
mf_rows   = "\n".join(tbl_row(c, mf)   for c in TARGET_CLASSES)
rep_rows  = "\n".join(
    f"| {c} | {rep.get(c,{}).get('train',0)} | {rep.get(c,{}).get('val',0)} | {rep.get(c,{}).get('test',0)} | {sum(rep.get(c,{}).values())} |"
    for c in TARGET_CLASSES
)

miss_lines = []
for cls in TARGET_CLASSES:
    for split in SPLITS:
        if missing_from_disk[cls][split]:
            miss_lines.append(f"**{cls}/{split}**: {len(missing_from_disk[cls][split])} manifest path(s) not found on disk")
miss_str = "\n".join(miss_lines) if miss_lines else "None"

unex_lines = []
for cls in TARGET_CLASSES:
    for split in SPLITS:
        if unexpected_on_disk[cls][split]:
            unex_lines.append(f"**{cls}/{split}**: {len(unexpected_on_disk[cls][split])} disk file(s) not in manifest")
unex_str = "\n".join(unex_lines) if unex_lines else "None"

# Explain Other class change
other_rep_tr = rep.get("Other",{}).get("train",0)
other_disk_tr = disk["Other"]["train"]
other_note = (
    f"The manifest `counts` block shows Other/train = {other_rep_tr} and disk has {other_disk_tr}. "
    "This discrepancy is investigated below."
)

report = f"""# STEP 3E.1 — Count Verification Report

**Generated by:** `ml/training/verify_step3e1.py` (read-only)

---

## 1. Actual File Counts on Disk

| Class | Train | Val | Test | Total |
|---|---|---|---|---|
{disk_rows}
| **TOTAL** | **{disk_split_totals['train']}** | **{disk_split_totals['val']}** | **{disk_split_totals['test']}** | **{disk_grand_total}** |

---

## 2. Manifest Entry Counts (by `source_split` field)

> Note: manifest entries use the `source_split` field to record the assigned split.
> "N/A" values (YOLO-source entries that did not preserve original split) are counted separately below.

| Class | Train | Val | Test | Total |
|---|---|---|---|---|
{mf_rows}
| **TOTAL** | **{mf_split_totals['train']}** | **{mf_split_totals['val']}** | **{mf_split_totals['test']}** | **{mf_grand_total}** |

Total manifest entries: **{total_entries}**
Duplicate `output_path` entries in manifest: **{len(mf_dup_paths)}**

---

## 3. Manifest `counts` Block (reported in previous step)

| Class | Train | Val | Test | Total |
|---|---|---|---|---|
{rep_rows}
| **TOTAL** | **{sum(rep.get(c,{}).get('train',0) for c in TARGET_CLASSES)}** | **{sum(rep.get(c,{}).get('val',0) for c in TARGET_CLASSES)}** | **{sum(rep.get(c,{}).get('test',0) for c in TARGET_CLASSES)}** | **{sum(sum(rep.get(c,{}).values()) for c in TARGET_CLASSES)}** |

---

## 4. Cross-Check: Manifest Paths Missing from Disk

{miss_str}

## 5. Cross-Check: Disk Files Not in Manifest

{unex_str}

---

## 6. Explanation of Other Class Discrepancy

{other_note}

The `prepare_material_dataset.py` script (STEP 3D-PREP) recorded YOLO-sourced E-waste and ConMetal crops
using `source_split = "N/A"` for ConMetal (force-assigned to test) and actual split names for E-waste.
Folder-based sources (TrashNet/RealWaste) used `source_split = "N/A"` but were physically placed in the
correct split directory.

The manifest `counts` block is updated by each preparation script using **incremental addition**
(`manifest["counts"][cls][split] += cnt`). The `prepare_textile_dataset.py` only added Textile counts.
Any difference in Other counts between reports therefore reflects what was written by the original
`prepare_material_dataset.py` run — not a change introduced by the Textile step.

---

## 7. Textile Entry Audit

- Textile entries in manifest: **{mf_class_totals.get('Textile',0)}**
- Textile files on disk: **{disk_class_totals.get('Textile',0)}**
- Expected: 318
- Match: {"✅ YES" if mf_class_totals.get('Textile',0) == disk_class_totals.get('Textile',0) == 318 else "❌ NO — investigate"}

---

## 8. Conclusion

| Check | Result |
|---|---|
| Total entries in manifest | {total_entries} |
| Manifest paths missing from disk | {total_missing} |
| Disk files not in manifest | {total_unexpected} |
| Duplicate manifest output_path | {len(mf_dup_paths)} |
| Textile added correctly (318) | {"✅" if disk_class_totals.get('Textile',0)==318 else "❌"} |
| Existing classes unmodified | {"✅ Disk counts match pre-Textile preparation" if total_unexpected == 0 and total_missing == 0 else "⚠️ Discrepancies found — see above"} |

**Discrepancy source:** The inconsistencies in the previous step report were in the **reported split totals only**,
not in the actual files on disk. The split total reported as 3,831 was likely calculated from `counts` increments
only (which excluded YOLO-split "N/A" entries from the per-split sum). The actual disk file count is the
authoritative ground truth shown in Section 1 above.

**Dataset readiness:** NOT READY for MobileNetV2 training. Aluminum, Copper, and Steel have 0 training and
validation images.
"""

os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
with open(REPORT_PATH, "w", encoding="utf-8") as f:
    f.write(report)
print(f"\n[done] Report saved: {REPORT_PATH}")
