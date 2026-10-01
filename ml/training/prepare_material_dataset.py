import os
import glob
import hashlib
import json
import random
import shutil
from datetime import datetime
from PIL import Image, UnidentifiedImageError

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATASET_DIR = os.path.join(BASE_DIR, "datasets", "material_images")
RAW_DATA_DIR = os.path.join(BASE_DIR, "datasets", "raw_sources")
MANIFEST_PATH = os.path.join(DATASET_DIR, "dataset_manifest.json")
REPORT_PATH = os.path.join(BASE_DIR, "ml", "reports", "material_dataset_preparation_report.md")

TARGET_CLASSES = [
    "Plastic", "Aluminum", "Copper", "Steel", "Paper",
    "Glass", "Textile", "E-waste", "Cardboard", "Other"
]
SPLITS = ["train", "val", "test"]
RANDOM_SEED = 42
random.seed(RANDOM_SEED)

def get_hash(filepath):
    h = hashlib.md5()
    try:
        with open(filepath, 'rb') as f:
            h.update(f.read())
        return h.hexdigest()
    except Exception:
        return None

def setup_directories():
    for split in SPLITS:
        for cls in TARGET_CLASSES:
            os.makedirs(os.path.join(DATASET_DIR, split, cls), exist_ok=True)

def parse_yolo_label(line, img_w, img_h):
    parts = line.strip().split()
    if len(parts) < 5: return None
    class_id = int(parts[0])
    xc, yc, w, h = map(float, parts[1:5])
    
    # Convert to pixel coordinates
    px_xc = xc * img_w
    px_yc = yc * img_h
    px_w = w * img_w
    px_h = h * img_h
    
    left = max(0, int(px_xc - px_w / 2))
    top = max(0, int(px_yc - px_h / 2))
    right = min(img_w, int(px_xc + px_w / 2))
    bottom = min(img_h, int(px_yc + px_h / 2))
    
    if right <= left or bottom <= top:
        return None
        
    return class_id, (left, top, right, bottom)

def prepare_dataset():
    setup_directories()
    
    manifest_entries = []
    global_hashes = set()
    
    stats = {
        "TrashNet": {"images": 0, "duplicates": 0, "corrupted": 0},
        "RealWaste": {"images": 0, "duplicates": 0, "corrupted": 0},
        "E-waste": {"images": 0, "crops": 0, "invalid": 0, "corrupted": 0},
        "ConMetal-6": {"images": 0, "crops": 0, "invalid": 0, "corrupted": 0}
    }
    
    target_counts = {cls: {"train": 0, "val": 0, "test": 0} for cls in TARGET_CLASSES}
    
    print("=== Processing Folder-Based Datasets ===")
    
    # TRASHNET & REALWASTE
    folder_sources = [
        {
            "name": "TrashNet",
            "dir": os.path.join(RAW_DATA_DIR, "trashnet"),
            "license": "MIT",
            "map": {
                "plastic": "Plastic", "paper": "Paper", "glass": "Glass", 
                "cardboard": "Cardboard", "trash": "Other"
            }
        },
        {
            "name": "RealWaste",
            "dir": os.path.join(RAW_DATA_DIR, "realwaste"),
            "license": "CC BY 4.0",
            "map": {
                "Plastic": "Plastic", "Paper": "Paper", "Glass": "Glass", 
                "Cardboard": "Cardboard", "Textile Trash": "Textile", 
                "Miscellaneous Trash": "Other"
            }
        }
    ]
    
    for src in folder_sources:
        if not os.path.exists(src["dir"]):
            print(f"[-] {src['name']} missing at {src['dir']}")
            continue
            
        print(f"[+] Processing {src['name']}...")
        
        # Collect images to split later (grouping not needed since 1 file = 1 image)
        valid_files = []
        for orig_cls, tgt_cls in src["map"].items():
            cls_dir = os.path.join(src["dir"], orig_cls)
            if not os.path.exists(cls_dir): continue
            
            for file in os.listdir(cls_dir):
                filepath = os.path.join(cls_dir, file)
                if not os.path.isfile(filepath): continue
                
                # Check corrupted
                try:
                    with Image.open(filepath) as img:
                        img.verify()
                except Exception:
                    stats[src["name"]]["corrupted"] += 1
                    continue
                    
                # Check duplicate
                h = get_hash(filepath)
                if not h or h in global_hashes:
                    stats[src["name"]]["duplicates"] += 1
                    continue
                global_hashes.add(h)
                
                valid_files.append((filepath, orig_cls, tgt_cls, h))
        
        # Shuffle and split 70/15/15
        random.shuffle(valid_files)
        n = len(valid_files)
        n_tr, n_v = int(n * 0.7), int(n * 0.15)
        
        for i, (filepath, orig_cls, tgt_cls, h) in enumerate(valid_files):
            split = "train" if i < n_tr else ("val" if i < n_tr + n_v else "test")
            
            filename = f"{src['name'].lower()}_{split}_{i:05d}{os.path.splitext(filepath)[1]}"
            out_path = os.path.join(DATASET_DIR, split, tgt_cls, filename)
            shutil.copy2(filepath, out_path)
            
            stats[src["name"]]["images"] += 1
            target_counts[tgt_cls][split] += 1
            
            with Image.open(out_path) as img:
                w, h_img = img.size
                
            manifest_entries.append({
                "source": src["name"],
                "original_image": filepath,
                "original_class": orig_cls,
                "target_class": tgt_cls,
                "source_split": "N/A",
                "output_path": out_path,
                "image_dimensions": [w, h_img],
                "source_license": src["license"]
            })

    print("\n=== Processing YOLO-Based Datasets ===")
    
    yolo_sources = [
        {
            "name": "E-waste",
            "dir": os.path.join(RAW_DATA_DIR, "ewaste", "E-Waste Dataset (2)"),
            "license": "CC BY 4.0",
            "splits": ["train", "valid", "test"], # Map valid -> val
            "map": {
                0: ("Battery_Waste", "E-waste"),
                2: ("Keyboard", "E-waste"),
                3: ("Light_Bulb", "E-waste"),
                6: ("Mobile", "E-waste"),
                7: ("Mouse", "E-waste"),
                9: ("PCB", "E-waste")
            },
            "force_split": None # Preserve source splits
        },
        {
            "name": "ConMetal-6",
            "dir": os.path.join(RAW_DATA_DIR, "conmetal6", "ConMetal-6-subset"),
            "license": "CC BY 4.0",
            "splits": ["eval"], # Assuming all are in one folder, or we treat entire thing as eval
            "map": {
                0: ("Aluminium", "Aluminum"),
                2: ("Copper", "Copper"),
                4: ("Galvanized Steel", "Steel"),
                5: ("Stainless Steel", "Steel")
            },
            "force_split": "test" # CRITICAL: Do NOT put in train. 
        }
    ]
    
    for src in yolo_sources:
        if not os.path.exists(src["dir"]):
            print(f"[-] {src['name']} missing at {src['dir']}")
            continue
            
        print(f"[+] Processing {src['name']}...")
        
        # YOLO structure varies. We'll search for images/ and labels/
        # Check standard YOLOv8 format: e.g., train/images, train/labels OR images/train, labels/train
        # For simplicity, we walk through the directory looking for .txt files in a 'labels' folder
        
        labels_found = glob.glob(os.path.join(src["dir"], "**", "labels", "**", "*.txt"), recursive=True)
        if not labels_found:
            # Fallback if structure is different
            labels_found = glob.glob(os.path.join(src["dir"], "**", "*.txt"), recursive=True)
        
        for lbl_path in labels_found:
            # Skip if it's classes.txt or data.yaml
            if os.path.basename(lbl_path) in ["classes.txt", "data.yaml", "README.md"]:
                continue
                
            img_path = lbl_path.replace("labels", "images").replace(".txt", ".jpg")
            if not os.path.exists(img_path):
                img_path = img_path.replace(".jpg", ".png")
                if not os.path.exists(img_path):
                    continue
            
            stats[src["name"]]["images"] += 1
            
            try:
                with Image.open(img_path) as img:
                    img_w, img_h = img.size
                    img.verify()
                # Reopen to crop
                orig_img = Image.open(img_path)
            except Exception:
                stats[src["name"]]["corrupted"] += 1
                continue
            
            # Determine split
            if src["force_split"]:
                out_split = src["force_split"]
            else:
                # E-waste dataset already has splits. Determine from path
                if "train" in lbl_path.lower(): out_split = "train"
                elif "valid" in lbl_path.lower() or "val" in lbl_path.lower(): out_split = "val"
                elif "test" in lbl_path.lower(): out_split = "test"
                else: out_split = "val" # default safety
            
            with open(lbl_path, "r") as f:
                lines = f.readlines()
                
            crop_idx = 0
            for line in lines:
                parsed = parse_yolo_label(line, img_w, img_h)
                if not parsed:
                    stats[src["name"]]["invalid"] += 1
                    continue
                cls_id, box = parsed
                
                if cls_id not in src["map"]:
                    continue # Excluded class
                    
                orig_cls, tgt_cls = src["map"][cls_id]
                left, top, right, bottom = box
                
                # Minimum area check
                if (right - left) < 10 or (bottom - top) < 10:
                    stats[src["name"]]["invalid"] += 1
                    continue
                    
                crop_img = orig_img.crop((left, top, right, bottom))
                
                # Check for uniqueness of this crop? Typically crops from same image are unique.
                # Data leakage prevention: YOLO objects from same image ALWAYS go to same out_split.
                
                dest_name = f"{src['name'].lower().replace(' ','_')}_{out_split}_{os.path.basename(img_path).split('.')[0]}_{crop_idx}.jpg"
                dest_path = os.path.join(DATASET_DIR, out_split, tgt_cls, dest_name)
                
                crop_img.convert("RGB").save(dest_path, "JPEG")
                
                stats[src["name"]]["crops"] += 1
                target_counts[tgt_cls][out_split] += 1
                
                manifest_entries.append({
                    "source": src["name"],
                    "original_image": img_path,
                    "original_class": orig_cls,
                    "target_class": tgt_cls,
                    "source_split": "N/A" if src["force_split"] else out_split,
                    "output_path": dest_path,
                    "crop_box": box,
                    "image_dimensions": [right - left, bottom - top],
                    "source_license": src["license"]
                })
                crop_idx += 1


    # Write Manifest
    manifest = {
        "creation_timestamp": datetime.now().isoformat(),
        "random_seed": RANDOM_SEED,
        "entries": manifest_entries,
        "counts": target_counts,
        "stats": stats
    }
    
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=4)
        
    # Write Report
    report_md = f"""# STEP 3D-PREP: Material Dataset Preparation Report
Generated: {manifest['creation_timestamp']}

## 1. Images Processed
* **TrashNet**: {stats["TrashNet"]["images"]} images processed ({stats["TrashNet"]["duplicates"]} duplicates, {stats["TrashNet"]["corrupted"]} corrupted).
* **RealWaste**: {stats["RealWaste"]["images"]} images processed ({stats["RealWaste"]["duplicates"]} duplicates, {stats["RealWaste"]["corrupted"]} corrupted).
* **E-waste**: {stats["E-waste"]["crops"]} valid crops extracted from {stats["E-waste"]["images"]} images.
* **ConMetal-6**: {stats["ConMetal-6"]["crops"]} evaluation crops extracted from {stats["ConMetal-6"]["images"]} images. (Strictly placed in TEST split, NO training data).

## 2. Counts per Target Class
| Class | Train | Val | Test | Total |
|-------|-------|-----|------|-------|
"""
    for cls in TARGET_CLASSES:
        tc = target_counts[cls]
        total = tc['train'] + tc['val'] + tc['test']
        report_md += f"| {cls} | {tc['train']} | {tc['val']} | {tc['test']} | {total} |\n"

    report_md += """
## 3. Excluded Classes
* TrashNet/RealWaste 'Metal' excluded (cannot reliably map to specific metals).
* RealWaste 'Food Waste', 'Vegetation' excluded.
* E-waste 'Glass_Waste', 'Medical_Waste', 'Metal_Waste', 'Organic_Waste', 'Paper_Waste', 'Plastic_Waste' excluded.
* ConMetal-6 'Brass', 'Ferrous Metal' excluded.

## 4. Quality & Data Leakage Checks
* Duplicates removed via MD5 hash (for full images).
* Corrupted files and zero/tiny area YOLO crops rejected.
* Leakage Prevention: E-waste objects from the same source image are strictly kept within their original source split (train -> train, valid -> val, test -> test).
* ConMetal-6 objects are strictly placed in the TEST split to prevent evaluation data from leaking into training.

## 5. Missing Classes & Readiness
**Are Aluminum, Copper, and Steel training images available?**
**NO.** The training counts for Aluminum, Copper, and Steel are 0. The ConMetal-6 dataset explicitly only provides evaluation data in this subset.

**Is the dataset ready for MobileNetV2 training?**
**NO.** Training cannot commence until training data for Aluminum, Copper, and Steel is acquired.
"""
    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report_md)

    print("\n=== Dataset Preparation Complete ===")
    print(f"Manifest written to {MANIFEST_PATH}")
    print(f"Report written to {REPORT_PATH}")

if __name__ == "__main__":
    prepare_dataset()
