"""
STEP 3E.1 — Prepare and add RealWaste Textile Trash images to the material dataset.

Source  : datasets/raw_sources/realwaste_textile/Textile Trash/
Target  : datasets/material_images/{train,val,test}/Textile/
Manifest: datasets/material_images/dataset_manifest.json

Rules enforced
--------------
* Source files are NEVER moved, renamed, or deleted.
* Existing prepared images (all other classes) are NEVER touched.
* No ConMetal evaluation images are touched.
* No synthetic images. No fabricated labels.
* SHA-256 deduplication against all images already in the prepared dataset.
* All images from the same source have no pre-existing split; apply 70/15/15
  with seed=42 and a documented rounding strategy.
* Idempotent: running twice is safe (hashes already present → skipped).
"""

import os
import hashlib
import json
import shutil
import random
from datetime import datetime
from PIL import Image, UnidentifiedImageError

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SOURCE_DIR  = os.path.join(BASE_DIR, "datasets", "raw_sources",
                           "realwaste_textile", "Textile Trash")
DATASET_DIR = os.path.join(BASE_DIR, "datasets", "material_images")
MANIFEST    = os.path.join(DATASET_DIR, "dataset_manifest.json")
REPORT_PATH = os.path.join(BASE_DIR, "ml", "reports",
                           "material_dataset_preparation_report.md")

TARGET_CLASS     = "Textile"
SOURCE_NAME      = "RealWaste"
ORIG_CLASS       = "Textile Trash"
SOURCE_URL       = "https://github.com/sam-single/realwaste"
LICENSE          = "CC BY 4.0"
RANDOM_SEED      = 42
TRAIN_RATIO      = 0.70
VAL_RATIO        = 0.15
# TEST_RATIO is the remainder so counts always sum to total

ALLOWED_EXT      = {".jpg", ".jpeg", ".png", ".webp"}
MIN_CROP_DIM     = 10   # px — reject zero/tiny images


# ── Helpers ───────────────────────────────────────────────────────────────────

def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load_existing_hashes(dataset_dir: str) -> set:
    """Hash every image already present in the prepared dataset."""
    seen = set()
    for split in ("train", "val", "test"):
        split_dir = os.path.join(dataset_dir, split)
        if not os.path.isdir(split_dir):
            continue
        for cls_folder in os.listdir(split_dir):
            cls_dir = os.path.join(split_dir, cls_folder)
            if not os.path.isdir(cls_dir):
                continue
            for fname in os.listdir(cls_dir):
                fpath = os.path.join(cls_dir, fname)
                if not os.path.isfile(fpath):
                    continue
                ext = os.path.splitext(fname)[1].lower()
                if ext in ALLOWED_EXT:
                    seen.add(sha256(fpath))
    print(f"[info] Loaded {len(seen)} existing hashes from prepared dataset.")
    return seen


def load_manifest(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_manifest(manifest: dict, path: str):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=4)


# ── Main ──────────────────────────────────────────────────────────────────────

def prepare_textile():
    random.seed(RANDOM_SEED)
    print("=== STEP 3E.1 — Adding Textile Trash images ===")

    # 1. Ensure target directories exist
    for split in ("train", "val", "test"):
        os.makedirs(os.path.join(DATASET_DIR, split, TARGET_CLASS), exist_ok=True)

    # 2. Load existing hashes (idempotency + cross-class deduplication)
    existing_hashes = load_existing_hashes(DATASET_DIR)

    # 3. Collect + validate source images
    all_files = sorted(os.listdir(SOURCE_DIR))   # deterministic order
    valid_images = []        # (fname, full_path, fhash, w, h)
    corrupted    = []
    unsupported  = []
    skipped_dup  = []

    for fname in all_files:
        src_path = os.path.join(SOURCE_DIR, fname)
        if not os.path.isfile(src_path):
            continue
        ext = os.path.splitext(fname)[1].lower()
        if ext not in ALLOWED_EXT:
            unsupported.append(fname)
            continue

        # PIL validation
        try:
            with Image.open(src_path) as img:
                img.verify()
            with Image.open(src_path) as img:
                w, h = img.size
        except (UnidentifiedImageError, OSError, Exception) as e:
            corrupted.append((fname, str(e)))
            continue

        if w < MIN_CROP_DIM or h < MIN_CROP_DIM:
            corrupted.append((fname, f"Image too small: {w}x{h}"))
            continue

        fhash = sha256(src_path)

        if fhash in existing_hashes:
            skipped_dup.append(fname)
            continue

        valid_images.append((fname, src_path, fhash, w, h))

    print(f"[info] Source files   : {len(all_files)}")
    print(f"[info] Valid images   : {len(valid_images)}")
    print(f"[info] Corrupted      : {len(corrupted)}")
    print(f"[info] Unsupported    : {len(unsupported)}")
    print(f"[info] Skipped (dup)  : {len(skipped_dup)}")

    n = len(valid_images)
    if n == 0:
        print("[warn] No valid images to add. Exiting.")
        return

    # 4. Deterministic 70 / 15 / 15 split
    #    Rounding strategy: floor train and val, test gets the remainder
    #    so counts always sum exactly to n.
    random.shuffle(valid_images)          # seeded above
    n_train = int(n * TRAIN_RATIO)        # floor
    n_val   = int(n * VAL_RATIO)          # floor
    n_test  = n - n_train - n_val         # remainder (≥ 0)

    print(f"[info] Split (seed={RANDOM_SEED}): train={n_train}, val={n_val}, test={n_test}, total={n_train+n_val+n_test}")
    assert n_train + n_val + n_test == n, "Split rounding error"

    slices = {
        "train": valid_images[:n_train],
        "val":   valid_images[n_train : n_train + n_val],
        "test":  valid_images[n_train + n_val:],
    }

    # 5. Copy images + build new manifest entries
    manifest = load_manifest(MANIFEST)
    new_entries     = []
    copied_counts   = {"train": 0, "val": 0, "test": 0}
    intra_hashes    = set()   # guard against src duplicates within this batch
    skipped_intra   = []

    for split, images in slices.items():
        dest_dir = os.path.join(DATASET_DIR, split, TARGET_CLASS)
        for i, (fname, src_path, fhash, w, h) in enumerate(images):
            if fhash in intra_hashes:
                skipped_intra.append(fname)
                continue
            intra_hashes.add(fhash)

            # Safe deterministic filename
            stem = os.path.splitext(fname)[0].replace(" ", "_")
            dest_name = f"realwaste_textile_{split}_{stem}.jpg"
            dest_path = os.path.join(dest_dir, dest_name)

            # Idempotent: skip if already copied (e.g. script re-run)
            if os.path.exists(dest_path):
                existing_hashes.add(fhash)
                copied_counts[split] += 1
                continue

            shutil.copy2(src_path, dest_path)
            existing_hashes.add(fhash)
            copied_counts[split] += 1

            new_entries.append({
                "source":                SOURCE_NAME,
                "source_dataset":        SOURCE_NAME,
                "original_image":        src_path,
                "source_image":          src_path,
                "original_class":        ORIG_CLASS,
                "source_original_class": ORIG_CLASS,
                "target_class":          TARGET_CLASS,
                "source_split":          split,
                "output_path":           dest_path,
                "sha256":                fhash,
                "width":                 w,
                "height":                h,
                "source_license":        LICENSE,
                "license":               LICENSE,
                "source_url":            SOURCE_URL,
                "mapping_decision":      "Textile Trash → Textile (direct mapping)"
            })

    # 6. Merge entries into manifest (append only; do not overwrite other classes)
    manifest["entries"].extend(new_entries)

    # Update per-class counts
    for split, cnt in copied_counts.items():
        manifest["counts"][TARGET_CLASS][split] += cnt

    manifest["textile_preparation"] = {
        "timestamp":           datetime.now().isoformat(),
        "source":              SOURCE_URL,
        "license":             LICENSE,
        "original_class":      ORIG_CLASS,
        "target_class":        TARGET_CLASS,
        "random_seed":         RANDOM_SEED,
        "train_ratio":         TRAIN_RATIO,
        "val_ratio":           VAL_RATIO,
        "test_ratio":          round(1 - TRAIN_RATIO - VAL_RATIO, 4),
        "rounding_strategy":   "floor(train), floor(val), remainder→test",
        "source_total":        len(all_files),
        "valid_images":        n,
        "train_count":         copied_counts["train"],
        "val_count":           copied_counts["val"],
        "test_count":          copied_counts["test"],
        "corrupted":           [c[0] for c in corrupted],
        "unsupported":         unsupported,
        "skipped_duplicates":  skipped_dup + skipped_intra,
        "source_preserved":    True
    }

    save_manifest(manifest, MANIFEST)
    print(f"[info] Manifest updated — {len(new_entries)} new entries added.")

    # 7. Print final table
    print("\n=== Class Counts After Textile Addition ===")
    print(f"{'Class':<12} {'Train':>7} {'Val':>7} {'Test':>7} {'Total':>7}")
    print("-" * 42)
    for cls, splits in manifest["counts"].items():
        tr, v, te = splits["train"], splits["val"], splits["test"]
        print(f"{cls:<12} {tr:>7} {v:>7} {te:>7} {tr+v+te:>7}")

    # 8. Write/update preparation report
    write_report(manifest, copied_counts, corrupted, unsupported, skipped_dup + skipped_intra, n)

    print(f"\n[done] Train/Val/Test Textile added: {copied_counts}")


def write_report(manifest, copied_counts, corrupted, unsupported, skipped_dups, n_valid):
    counts = manifest["counts"]
    rows = ""
    for cls, splits in counts.items():
        tr, v, te = splits["train"], splits["val"], splits["test"]
        rows += f"| {cls} | {tr} | {v} | {te} | {tr+v+te} |\n"

    report = f"""# Material Dataset Preparation Report — STEP 3E.1 (Textile Addition)

**Updated:** {datetime.now().isoformat()}

## Textile Source Details
| Field | Value |
|---|---|
| Source dataset | RealWaste |
| Source URL | https://github.com/sam-single/realwaste |
| License | CC BY 4.0 |
| Original class name | Textile Trash |
| Target class | Textile |
| Source images | 318 |
| Valid images processed | {n_valid} |
| Train added | {copied_counts['train']} |
| Val added | {copied_counts['val']} |
| Test added | {copied_counts['test']} |
| Duplicates skipped | {len(skipped_dups)} |
| Corrupted skipped | {len(corrupted)} |
| Unsupported skipped | {len(unsupported)} |

## Split Method
- Random seed: 42
- Ratios: 70% train / 15% val / 15% test
- Rounding: `floor(n × 0.70)` train, `floor(n × 0.15)` val, remainder → test
- This guarantees counts sum exactly to total valid images.

## Data Integrity
- Original source files preserved at `datasets/raw_sources/realwaste_textile/Textile Trash/`
- SHA-256 deduplication performed against all existing prepared images before copying.
- Idempotent: re-running the script is safe (existing hashes are skipped).
- No images from other classes were modified.
- No ConMetal evaluation images were touched.
- No synthetic images or fabricated labels.

## Full Dataset Class Table
| Class | Train | Val | Test | Total |
|---|---|---|---|---|
{rows}
## MobileNetV2 Readiness
**NOT READY.** Aluminum, Copper, and Steel still have 0 training and validation images.
The ConMetal-6 evaluation images remain strictly in test only.
Model training must not begin until all 10 classes have training and validation data.
"""
    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"[info] Report saved to {REPORT_PATH}")


if __name__ == "__main__":
    prepare_textile()
