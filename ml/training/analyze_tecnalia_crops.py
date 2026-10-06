import os
import numpy as np
from PIL import Image
from scipy.ndimage import label, find_objects

DATA_DIR = r"C:\Users\jenit\Downloads\dataset_tecnalia_weee_1_0_4\dataset\data"

LABELS = {
    1: "Copper",
    3: "Aluminum",
    5: "Stainless Steel"
}

MIN_CROP_DIM = 30

def analyze_dataset():
    if not os.path.exists(DATA_DIR):
        print(f"Error: {DATA_DIR} not found.")
        return

    files = [f for f in os.listdir(DATA_DIR) if f.endswith("_gt.png")]
    
    stats = {
        "Copper": {"count": 0, "valid": 0, "too_small": 0, "sizes": []},
        "Aluminum": {"count": 0, "valid": 0, "too_small": 0, "sizes": []},
        "Stainless Steel": {"count": 0, "valid": 0, "too_small": 0, "sizes": []}
    }
    
    total_images = len(files)
    print(f"Analyzing {total_images} ground truth files...")
    
    for filename in files:
        filepath = os.path.join(DATA_DIR, filename)
        try:
            img = Image.open(filepath).convert('L')
            img_arr = np.array(img)
        except Exception as e:
            print(f"Could not read {filename}: {e}")
            continue
            
        for val, name in LABELS.items():
            mask = (img_arr == val).astype(int)
            labeled_array, num_features = label(mask)
            
            if num_features > 0:
                objects = find_objects(labeled_array)
                for obj in objects:
                    # obj is a tuple of slices (slice_y, slice_x)
                    h = obj[0].stop - obj[0].start
                    w = obj[1].stop - obj[1].start
                    
                    stats[name]["count"] += 1
                    stats[name]["sizes"].append((w, h))
                    
                    if w < MIN_CROP_DIM or h < MIN_CROP_DIM:
                        stats[name]["too_small"] += 1
                    else:
                        stats[name]["valid"] += 1

    print("\n--- Summary ---")
    for name, data in stats.items():
        print(f"\n{name}:")
        print(f"  Total objects: {data['count']}")
        print(f"  Valid (>={MIN_CROP_DIM}px): {data['valid']}")
        print(f"  Too small: {data['too_small']}")
        if data["sizes"]:
            widths = [s[0] for s in data["sizes"]]
            heights = [s[1] for s in data["sizes"]]
            print(f"  Width range: {min(widths)} - {max(widths)} px")
            print(f"  Height range: {min(heights)} - {max(heights)} px")

if __name__ == "__main__":
    analyze_dataset()
