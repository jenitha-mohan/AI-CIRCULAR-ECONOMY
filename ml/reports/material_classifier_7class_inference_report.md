# STEP 3G — 7-Class Material Classifier Inference Verification Report

**Generated:** 2026-10-12  
**Model:** `ml/models/material_classifier_mobilenetv2_7class.pth`  
**Metadata:** `ml/models/material_classifier_7class_metadata.json`  
**Inference script:** `ml/inference/predict_material.py`  
**Verification script:** `ml/inference/verify_inference.py`

> [!IMPORTANT]
> **PROTOTYPE ONLY.** This model classifies 7 materials. Aluminum, Copper, and Steel are excluded — they have no training or validation data and cannot be reliably predicted.

---

## 1. Architecture and Configuration Verification

| Field | Training Script | Inference Script | Match |
|-------|----------------|-----------------|-------|
| Architecture | MobileNetV2 | MobileNetV2 | ✅ |
| Final layer | `Linear(1280 → 7)` | `Linear(1280 → num_classes)` from metadata | ✅ |
| Image size | 224×224 | 224×224 (read from metadata) | ✅ |
| Resize step | Resize(256) → CenterCrop(224) | Resize(256) → CenterCrop(224) | ✅ |
| Normalization | `mean=[0.485,0.456,0.406]` `std=[0.229,0.224,0.225]` | Same | ✅ |
| Class order | Sorted alphabetically by `TargetClassImageFolder` | Read from metadata JSON | ✅ |

**Confirmed class order in metadata:**
```
["Cardboard", "E-waste", "Glass", "Other", "Paper", "Plastic", "Textile"]
```

**Command-line interface:** Positional argument `image_path` (not `--image`):
```
python ml/inference/predict_material.py <image_path> [--model-path ...] [--metadata-path ...]
```

---

## 2. Commands Executed

```powershell
# Environment setup
$env:PYTHONIOENCODING="utf-8"

# Verification run (7 class images + 1 error test)
python ml\inference\verify_inference.py

# Individual inference example (from predict_material.py interface)
python ml\inference\predict_material.py datasets/material_images/test/Cardboard/realwaste_test_02376.jpg
```

---

## 3. Inference Results — All 7 Test Images

| # | True Class | Image File | Predicted | Confidence | Correct | All Probs Finite | Top-3 Ordered |
|---|-----------|-----------|-----------|-----------|---------|-----------------|--------------|
| 1 | Cardboard | `realwaste_test_02376.jpg` | **Cardboard** | 89.82% | ✅ | ✅ | ✅ |
| 2 | E-waste | `e-waste_test_IMG_20250803_215632_jpg_0.jpg` | **E-waste** | 99.88% | ✅ | ✅ | ✅ |
| 3 | Glass | `realwaste_test_02377.jpg` | **Glass** | 98.95% | ✅ | ✅ | ✅ |
| 4 | Other | `realwaste_test_02385.jpg` | **Other** | 71.77% | ✅ | ✅ | ✅ |
| 5 | Paper | `realwaste_test_02384.jpg` | Cardboard | 45.86% | ❌ | ✅ | ✅ |
| 6 | Plastic | `realwaste_test_02378.jpg` | **Plastic** | 82.35% | ✅ | ✅ | ✅ |
| 7 | Textile | `realwaste_textile_test_Textile_Trash_101.jpg` | **Textile** | 97.75% | ✅ | ✅ | ✅ |

**Result: 6/7 correct (85.7% on this sample)**

---

## 4. Per-Image Top-3 Predictions

### Image 1 — Cardboard [CORRECT]
```
Path: datasets/material_images/test/Cardboard/realwaste_test_02376.jpg
1. Cardboard — 89.82%
2. Paper     —  5.92%
3. Other     —  1.88%
```

### Image 2 — E-waste [CORRECT]
```
Path: datasets/material_images/test/E-waste/e-waste_test_IMG_20250803_215632_jpg_0.jpg
1. E-waste   — 99.88%
2. Paper     —  0.04%
3. Cardboard —  0.03%
```

### Image 3 — Glass [CORRECT]
```
Path: datasets/material_images/test/Glass/realwaste_test_02377.jpg
1. Glass    — 98.95%
2. Plastic  —  0.79%
3. Other    —  0.09%
```

### Image 4 — Other [CORRECT]
```
Path: datasets/material_images/test/Other/realwaste_test_02385.jpg
1. Other    — 71.77%
2. Plastic  — 11.84%
3. Textile  —  6.71%
```
*Note: Lower confidence is expected for "Other" — it is a catch-all class with mixed content.*

### Image 5 — Paper [WRONG — predicted Cardboard]
```
Path: datasets/material_images/test/Paper/realwaste_test_02384.jpg
1. Cardboard — 45.86%
2. Other     — 28.26%
3. Paper     — 19.88%
```
*Note: Paper/Cardboard confusion is the most common error in the test-set classification report (Cardboard recall = 76%, Paper precision = 81%). This specific image likely shows a flat brown surface that resembles corrugated cardboard packaging.*

### Image 6 — Plastic [CORRECT]
```
Path: datasets/material_images/test/Plastic/realwaste_test_02378.jpg
1. Plastic  — 82.35%
2. Other    —  9.86%
3. Paper    —  3.44%
```

### Image 7 — Textile [CORRECT]
```
Path: datasets/material_images/test/Textile/realwaste_textile_test_Textile_Trash_101.jpg
1. Textile  — 97.75%
2. Other    —  1.95%
3. Plastic  —  0.14%
```

---

## 5. Error Handling Test

**Input:** `datasets/material_images/test/Cardboard/NONEXISTENT_IMAGE.jpg`

**Expected behaviour:** Script detects missing file before attempting to open it, prints an error, and continues gracefully.

**Actual output:**
```
Image  : datasets/material_images/test/Cardboard/NONEXISTENT_IMAGE.jpg
True   : ERROR_TEST
Result : ERROR — file not found
```

**Error handling: PASSED.** The script does not crash; it prints a descriptive message and continues.

---

## 6. Numerical Verification

| Check | Result |
|-------|--------|
| All probabilities finite (no NaN/Inf) | ✅ All 7 images passed |
| Top-3 probabilities strictly descending | ✅ All 7 images passed |
| Probabilities sum to ~1.0 (softmax) | ✅ (guaranteed by `torch.nn.functional.softmax`) |
| Confidence values in `[0.0, 1.0]` | ✅ Range: 45.86% – 99.88% |

---

## 7. Known Issues and Limitations

| Issue | Detail |
|-------|--------|
| Windows cp1252 encoding | Unicode checkmarks (✓ ✗) cannot be printed without `PYTHONIOENCODING=utf-8`. Replaced with ASCII in verification script. |
| Paper/Cardboard confusion | Consistent with the training report (Paper F1 = 0.86, Cardboard F1 = 0.83). Brown flat-sheet materials are visually similar. |
| No Aluminum / Copper / Steel | These 3 classes have 0 training/validation images. If a user submits a metal image, the model will misclassify it as one of the 7 supported classes. |
| 3-epoch training only | The model was trained for 3 epochs due to CPU-only training time constraints (~27 min/epoch). More epochs would likely improve Paper/Cardboard separation. |

---

## 8. Inference Script Interface (predict_material.py)

```bash
# Positional argument — image_path is required
python ml/inference/predict_material.py <image_path>

# Optional arguments (defaults point to trained model)
python ml/inference/predict_material.py <image_path> \
  --model-path ml/models/material_classifier_mobilenetv2_7class.pth \
  --metadata-path ml/models/material_classifier_7class_metadata.json
```

**Example output:**
```
--- INFERENCE RESULT ---
WARNING: This is a 7-class prototype. Aluminum, Copper, and Steel are excluded.

Predicted material: Cardboard
Confidence: 0.8982

Top 3:
1. Cardboard - 0.8982
2. Paper - 0.0592
3. Other - 0.0188
```

---

## 9. Conclusion

Inference verification **PASSED**.

- Model checkpoint loads correctly from `ml/models/material_classifier_mobilenetv2_7class.pth`
- Architecture, class ordering, image size, and normalization all match the training configuration
- 6 of 7 sampled test images were predicted correctly (85.7% on this sample, consistent with 84.97% test accuracy from training)
- All probability outputs are finite and correctly ordered
- File-not-found error handling works correctly
- The inference script is **not integrated into the production backend** — the existing heuristic `classification_service.py` remains unchanged

**Next step:** STEP 3H — Integrate the real MobileNetV2 classifier into the FastAPI backend, replacing the heuristic RGB classifier, with appropriate fallback behaviour for the 3 missing metal classes.
