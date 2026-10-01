import os
import hashlib
from collections import defaultdict
from PIL import Image, UnidentifiedImageError

DATASET_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "datasets",
    "material_images"
)

TARGET_CLASSES = [
    "Plastic", "Aluminum", "Copper", "Steel", "Paper",
    "Glass", "Textile", "E-waste", "Cardboard", "Other"
]

SPLITS = ["train", "val", "test"]

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def get_file_hash(filepath):
    hasher = hashlib.md5()
    try:
        with open(filepath, 'rb') as f:
            buf = f.read()
            hasher.update(buf)
        return hasher.hexdigest()
    except Exception:
        return None


def audit_dataset():
    print("Starting Dataset Audit...\n")

    stats = {
        split: {cls: 0 for cls in TARGET_CLASSES}
        for split in SPLITS
    }
    
    total_images = 0
    unsupported_files = []
    corrupted_images = []
    
    # Hash -> List of file paths to detect duplicates
    file_hashes = defaultdict(list)
    duplicates = []

    if not os.path.exists(DATASET_DIR):
        print(f"Error: Dataset directory {DATASET_DIR} does not exist.")
        return

    for split in SPLITS:
        split_dir = os.path.join(DATASET_DIR, split)
        if not os.path.exists(split_dir):
            continue

        for cls in TARGET_CLASSES:
            cls_dir = os.path.join(split_dir, cls)
            if not os.path.exists(cls_dir):
                continue
                
            for root, _, files in os.walk(cls_dir):
                for file in files:
                    ext = os.path.splitext(file)[1].lower()
                    filepath = os.path.join(root, file)
                    
                    if ext not in ALLOWED_EXTENSIONS:
                        unsupported_files.append(filepath)
                        continue
                    
                    # Validate image
                    try:
                        with Image.open(filepath) as img:
                            img.verify()  # verify integrity
                        
                        # Re-open to get dimensions if needed (verify closes the file pointer in some PIL versions)
                        with Image.open(filepath) as img:
                            img.load()
                    except (UnidentifiedImageError, OSError):
                        corrupted_images.append(filepath)
                        continue
                        
                    # Hash for duplicate detection
                    file_hash = get_file_hash(filepath)
                    if file_hash:
                        file_hashes[file_hash].append(filepath)
                        if len(file_hashes[file_hash]) > 1:
                            duplicates.append((filepath, file_hashes[file_hash][0]))
                    
                    stats[split][cls] += 1
                    total_images += 1

    # Print Report
    print("Dataset Audit")
    print("-" * 25)
    
    total_per_class = {cls: 0 for cls in TARGET_CLASSES}
    
    for cls in TARGET_CLASSES:
        cls_total = sum(stats[split][cls] for split in SPLITS)
        total_per_class[cls] = cls_total
        print(f"{cls:<12}: {cls_total}")
        
    print(f"\nTotal: {total_images}\n")
    
    print("Split Details:")
    for split in SPLITS:
        split_total = sum(stats[split].values())
        print(f"  {split.capitalize()}: {split_total}")

    print("\nData Quality Issues:")
    print(f"  Unsupported files: {len(unsupported_files)}")
    print(f"  Corrupted images:  {len(corrupted_images)}")
    print(f"  Exact duplicates:  {len(duplicates)}")
    
    print("\nClass Imbalance Check:")
    if total_images == 0:
        print("  WARNING: Dataset is completely empty. Real images must be collected.")
    else:
        for cls, count in total_per_class.items():
            if count == 0:
                print(f"  CRITICAL: {cls} has 0 images.")
            elif count < 100:
                print(f"  WARNING: {cls} is severely underrepresented ({count} images).")

    print("\nAudit Complete.")


if __name__ == "__main__":
    audit_dataset()
