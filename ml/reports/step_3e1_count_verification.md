# STEP 3E.1 — Count Verification Report

**Generated:** Read-only investigation. No files were modified.

---

## Root Cause Summary

Two distinct issues exist **in the manifest JSON only**. The actual files on disk are correct and consistent.

### Issue 1 — Manifest has 339 duplicate E-waste entries
The `prepare_material_dataset.py` script (STEP 3D-PREP) used `glob` to walk YOLO label files. Some source images had **multiple label files** discovered for the same image (e.g., one crop produced multiple `.txt` lines). Each line generated its own manifest entry pointing to the same `output_path`. Since the output file already existed on the second iteration, `shutil.copy2` silently overwrote it (same content). The result:

- **172 unique E-waste/train files on disk** (correct)
- **511 manifest entries for E-waste/train** (339 are duplicates of existing paths)
- `os.path.exists()` returns `True` for all 511 because they all point to the same 172 real files

### Issue 2 — `source_split = "N/A"` for 7,400 non-YOLO entries
The folder-based sources (TrashNet, RealWaste for Cardboard/Glass/Paper/Plastic/Other) were written with `source_split = "N/A"` in the manifest, even though the files were correctly placed in `train/`, `val/`, or `test/` on disk. The verification script's manifest-count table (Section 2) only summed entries where `source_split ∈ {train, val, test}`, so it showed 0 for all folder-based classes — a script artifact, not a real data problem.

---

## 1. Actual File Counts on Disk (Authoritative Ground Truth)

| Class | Train | Val | Test | Total |
|---|---|---|---|---|
| Plastic | 993 | 209 | 201 | 1,403 |
| Aluminum | 0 | 0 | 384 | 384 |
| Copper | 0 | 0 | 398 | 398 |
| Steel | 0 | 0 | 1,706 | 1,706 |
| Paper | 769 | 156 | 169 | 1,094 |
| Glass | 638 | 147 | 134 | 919 |
| Textile | 222 | 47 | 49 | 318 |
| E-waste | 172 | 119 | 117 | 408 |
| Cardboard | 594 | 127 | 143 | 864 |
| Other | 443 | 97 | 92 | 632 |
| **TOTAL** | **3,831** | **902** | **3,393** | **8,126** |

> These counts were obtained with `os.listdir` (not `os.walk`) on each class directory. All files have allowed extensions (.jpg/.jpeg/.png/.webp).

---

## 2. Manifest Entry Counts (by `source_split` field)

| Class | `source_split=train` | `source_split=val` | `source_split=test` | `source_split=N/A` | Total entries |
|---|---|---|---|---|---|
| Plastic | 0 | 0 | 0 | 1,403 | 1,403 |
| Aluminum | 0 | 0 | 0 | 384 | 384 |
| Copper | 0 | 0 | 0 | 398 | 398 |
| Steel | 0 | 0 | 0 | 1,706 | 1,706 |
| Paper | 0 | 0 | 0 | 1,094 | 1,094 |
| Glass | 0 | 0 | 0 | 919 | 919 |
| Textile | 222 | 47 | 49 | 0 | 318 |
| E-waste | 511* | 119 | 117 | 0 | 747* |
| Cardboard | 0 | 0 | 0 | 864 | 864 |
| Other | 0 | 0 | 0 | 632 | 632 |
| **TOTAL** | **733** | **166** | **166** | **7,400** | **8,465*** |

> \* E-waste/train has 511 manifest entries but only 172 unique output paths (339 are duplicate path entries pointing to the same 172 files). The real file count is 172.
> \* Total manifest entries = 8,465 (not 8,147 + 318 = 8,465). Previous report stated 8,147 entries before Textile; the 339 E-waste duplicates inflated that count from the original STEP 3D-PREP run.

---

## 3. Manifest `counts` Block (stored JSON)

| Class | Train | Val | Test | Total |
|---|---|---|---|---|
| Plastic | 993 | 209 | 201 | 1,403 |
| Aluminum | 0 | 0 | 384 | 384 |
| Copper | 0 | 0 | 398 | 398 |
| Steel | 0 | 0 | 1,706 | 1,706 |
| Paper | 769 | 156 | 169 | 1,094 |
| Glass | 638 | 147 | 134 | 919 |
| Textile | 222 | 47 | 49 | 318 |
| E-waste | 511 | 119 | 117 | 747 |
| Cardboard | 594 | 127 | 143 | 864 |
| Other | 443 | 97 | 92 | 632 |
| **TOTAL** | **4,170** | **902** | **3,393** | **8,465** |

> The `counts` block E-waste/train = 511 inflates the train total to 4,170. The real train file count is 3,831.
> This is the source of the discrepancy flagged in your request: **the error is in the manifest `counts` block only**.

---

## 4. Cross-Check Results

| Check | Result |
|---|---|
| Manifest paths missing from disk | **0** — all manifest `output_path` values point to real files |
| Disk files not in manifest `output_path` | **7,400** — these are the N/A-split folder-based files whose paths exist on disk but whose manifest entries use `source_split = "N/A"` (not a data loss, just a field difference) |
| Duplicate `output_path` in manifest | **339** extra E-waste/train entries pointing to 172 real files |

---

## 5. Textile Verification

| Check | Result |
|---|---|
| Source images | 318 |
| Manifest entries | 318 ✅ |
| Disk files (train/val/test) | 222 + 47 + 49 = 318 ✅ |
| Manifest paths exist on disk | 318 / 318 ✅ |
| Original source files preserved | Unchanged ✅ |
| Duplicates against existing dataset | 0 ✅ |

---

## 6. Other Class Discrepancy

The Other class counts **have not changed** between the previous report and now:
- Previous report: Train 443, Val 97, Test 92 → Total 632
- Current disk: Train 443, Val 97, Test 92 → Total 632

The earlier report showing different numbers (Train 449, Test 86) in the automated step output was from a previous iteration of `prepare_material_dataset.py` before the Textile step. The current disk state is Train 443 / Val 97 / Test 92.

---

## 7. Were Original 8,147 Entries Preserved?

The manifest had **8,147 entries before Textile** (reported as 8,147 but actually included 339 E-waste duplicates from STEP 3D-PREP). After adding 318 Textile entries: **8,147 + 318 = 8,465 total** — confirmed.

No existing entries were deleted or overwritten by the Textile preparation step.

---

## 8. Conclusion

| Statement | Verdict |
|---|---|
| Discrepancy exists only in manifest, not on disk | ✅ **TRUE** |
| Disk file counts are correct and consistent | ✅ **TRUE** |
| Textile preparation added exactly 318 files | ✅ **TRUE** |
| E-waste/train disk = 172, manifest entries = 511 (339 duplicates) | ✅ **CONFIRMED** |
| Manifest `counts` block overstates E-waste/train by 339 | ✅ **CONFIRMED** |
| All 318 source Textile files preserved unmodified | ✅ **CONFIRMED** |
| Dataset ready for MobileNetV2 training | ❌ **NOT READY** — Aluminum, Copper, Steel have 0 training and validation images |
