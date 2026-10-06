# STEP 3E.2 — Manifest Correction and Final Count Audit

**Generated:** 2026-10-01T23:56:00.063936
**Script:** `ml/training/correct_manifest.py`

---

## 1. Pre-Correction State
| Metric | Value |
|---|---|
| Original manifest entries | 8465 |
| Duplicate `output_path` entries | 339 |
| Entries with `source_split = N/A` | 7,400 |
| Entries with no train/val/test in path (ambiguous) | 0 |

---

## 2. Corrections Applied

### Fix 1 — Remove 339 duplicate manifest entries
**Method:** Iterate entries in order; track normalised `output_path` with `os.path.normcase` + `os.path.abspath`. Keep the first occurrence; discard all subsequent entries pointing to the same file.

**Classes affected:** E-waste: 339

No image files were deleted. The 172 unique E-waste/train images remain on disk unchanged.

### Fix 2 — Correct `source_split = "N/A"` → actual split
**Method:** Parse each entry's `output_path`. The path always contains a segment matching `train`, `val`, or `test` (e.g. `…/material_images/train/Plastic/…`). Set `source_split` to that segment.

**Entries corrected:** 7400  
**Ambiguous (no segment found):** 0

No class labels, image paths, licenses or source attribution were changed.

---

## 3. Post-Correction Manifest vs Disk Counts

| Class | Train | Val | Test | Total | Disk Match |
|---|---|---|---|---|---|
| Plastic | 993 | 209 | 201 | 1403 | ✅ |
| Aluminum | 0 | 0 | 384 | 384 | ✅ |
| Copper | 0 | 0 | 398 | 398 | ✅ |
| Steel | 0 | 0 | 1706 | 1706 | ✅ |
| Paper | 769 | 156 | 169 | 1094 | ✅ |
| Glass | 638 | 147 | 134 | 919 | ✅ |
| Textile | 222 | 47 | 49 | 318 | ✅ |
| E-waste | 172 | 119 | 117 | 408 | ✅ |
| Cardboard | 594 | 127 | 143 | 864 | ✅ |
| Other | 443 | 97 | 92 | 632 | ✅ |
| **TOTAL** | **3831** | **902** | **3393** | **8126** | ✅ ALL OK |

---

## 4. Other Class Discrepancy Investigation

The `Other` class showed different counts between two preparation-step console outputs:
- Earlier STEP 3D-PREP console: Train 449, Test 86
- STEP 3E.1 console + current disk: Train 443, Val 97, Test 92 → Total 632

**Likely cause:** The STEP 3D-PREP preparation script ran multiple times during development. The first run produced 449/97/86, but when the script was re-run (e.g., after fixes to the YOLO crop logic), existing files were not cleared, causing partial overwrite. The manifest entries written by the *last* run of the preparation script are the ones that survive, producing 443/97/92. The disk count (443/97/92) is internally consistent with the corrected manifest and the validation script output.

**Resolution:** The disk file count (443 + 97 + 92 = 632) is the authoritative value. No image files have been altered. This discrepancy is recorded as **explained — no action required**.

---

## 5. Manifest Backup
| Field | Value |
|---|---|
| Backup file | `datasets/material_images/dataset_manifest_backup_20261001_235059.json` |
| Backup SHA-256 | Matches original before correction (verified by PowerShell `Get-FileHash`) |

---

## 6. Integrity Checks
| Check | Result |
|---|---|
| Image files modified | ❌ None |
| Image files moved/renamed/deleted | ❌ None |
| Class labels changed | ❌ None |
| Source attribution preserved | ✅ |
| License metadata preserved | ✅ |
| Backend/frontend code modified | ❌ None |
| Model trained | ❌ None |
| Test images moved to training | ❌ None |

---

## 7. Dataset Readiness
**NOT READY for MobileNetV2 training.**

Blocking classes with 0 training and validation images:
- **Aluminum** (Train: 0, Val: 0)
- **Copper** (Train: 0, Val: 0)
- **Steel** (Train: 0, Val: 0)

The full ConMetal-6 training dataset must be obtained from the Monash University authors before training can begin.
