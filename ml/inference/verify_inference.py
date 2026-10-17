"""
STEP 3G — Batch inference verification script.
Runs predict on 7 test images (one per class) + 1 nonexistent path error test.
Prints structured output for report generation.
Does NOT modify any model, dataset, or metadata.
"""
import os
import sys
import json
import math
import torch
from torchvision import transforms, models
from PIL import Image

MODEL_PATH    = "ml/models/material_classifier_mobilenetv2_7class.pth"
METADATA_PATH = "ml/models/material_classifier_7class_metadata.json"

TEST_IMAGES = [
    ("Cardboard", r"datasets/material_images/test/Cardboard/realwaste_test_02376.jpg"),
    ("E-waste",   r"datasets/material_images/test/E-waste/e-waste_test_IMG_20250803_215632_jpg_0.jpg"),
    ("Glass",     r"datasets/material_images/test/Glass/realwaste_test_02377.jpg"),
    ("Other",     r"datasets/material_images/test/Other/realwaste_test_02385.jpg"),
    ("Paper",     r"datasets/material_images/test/Paper/realwaste_test_02384.jpg"),
    ("Plastic",   r"datasets/material_images/test/Plastic/realwaste_test_02378.jpg"),
    ("Textile",   r"datasets/material_images/test/Textile/realwaste_textile_test_Textile_Trash_101.jpg"),
    ("ERROR_TEST", r"datasets/material_images/test/Cardboard/NONEXISTENT_IMAGE.jpg"),
]

# ── Load model ────────────────────────────────────────────────────────────────
if not os.path.exists(MODEL_PATH):
    print(f"FATAL: Model not found at {MODEL_PATH}")
    sys.exit(1)
if not os.path.exists(METADATA_PATH):
    print(f"FATAL: Metadata not found at {METADATA_PATH}")
    sys.exit(1)

with open(METADATA_PATH) as f:
    metadata = json.load(f)

class_names = metadata["class_names"]
num_classes  = metadata["num_classes"]
image_size   = metadata.get("image_size", 224)

print(f"Architecture : MobileNetV2")
print(f"Num classes  : {num_classes}")
print(f"Class order  : {class_names}")
print(f"Image size   : {image_size}x{image_size}")
print(f"Normalization: mean=[0.485,0.456,0.406]  std=[0.229,0.224,0.225]  (ImageNet)")
print()

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Device: {device}")

model = models.mobilenet_v2()
model.classifier[1] = torch.nn.Linear(model.last_channel, num_classes)
model.load_state_dict(torch.load(MODEL_PATH, map_location=device, weights_only=True))
model = model.to(device)
model.eval()
print("Model loaded successfully.\n")

transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(image_size),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])

# ── Run inference ─────────────────────────────────────────────────────────────
results = []
print("=" * 64)
for true_class, img_path in TEST_IMAGES:
    print(f"Image  : {img_path}")
    print(f"True   : {true_class}")

    if not os.path.exists(img_path):
        print(f"Result : ERROR — file not found")
        results.append({
            "true_class": true_class,
            "image_path": img_path,
            "error": "FileNotFoundError",
            "predicted": None,
            "confidence": None,
            "top3": None,
        })
        print("=" * 64)
        continue

    try:
        image = Image.open(img_path).convert("RGB")
    except Exception as e:
        print(f"Result : ERROR loading image — {e}")
        results.append({
            "true_class": true_class, "image_path": img_path,
            "error": str(e), "predicted": None, "confidence": None, "top3": None,
        })
        print("=" * 64)
        continue

    tensor = transform(image).unsqueeze(0).to(device)

    with torch.no_grad():
        logits = model(tensor)
        probs  = torch.nn.functional.softmax(logits[0], dim=0)

    sorted_probs, sorted_idx = torch.sort(probs, descending=True)

    # Verify all probabilities are finite
    all_finite = all(math.isfinite(p.item()) for p in probs)
    # Verify top-3 ordering
    ordering_ok = (sorted_probs[0] >= sorted_probs[1] >= sorted_probs[2])

    top3 = [(class_names[sorted_idx[i].item()], round(sorted_probs[i].item(), 6))
            for i in range(3)]

    pred_class  = top3[0][0]
    confidence  = top3[0][1]
    correct     = "[CORRECT]" if pred_class == true_class else "[WRONG]"

    print(f"Predicted : {pred_class} ({confidence*100:.2f}%)  {correct}")
    print(f"Top 3:")
    for rank, (cls, prob) in enumerate(top3, 1):
        print(f"  {rank}. {cls} — {prob*100:.2f}%")
    print(f"All probs finite : {all_finite}")
    print(f"Top-3 ordering OK: {ordering_ok}")
    print("=" * 64)

    results.append({
        "true_class":      true_class,
        "image_path":      img_path,
        "error":           None,
        "predicted":       pred_class,
        "correct":         pred_class == true_class,
        "confidence":      confidence,
        "top3":            top3,
        "all_finite":      all_finite,
        "ordering_ok":     ordering_ok,
    })

# ── Summary ───────────────────────────────────────────────────────────────────
valid = [r for r in results if r["error"] is None]
errors = [r for r in results if r["error"] is not None]
correct_count = sum(1 for r in valid if r["correct"])
print(f"\nSummary: {correct_count}/{len(valid)} correct  |  {len(errors)} error(s) (expected: 1)")

# Dump JSON for report
print("\n===JSON===")
import json as _j
print(_j.dumps(results, indent=2))
