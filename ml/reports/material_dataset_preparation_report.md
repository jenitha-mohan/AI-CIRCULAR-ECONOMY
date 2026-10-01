# STEP 3D-PREP: Material Dataset Preparation Report
Generated: 2026-09-29T23:42:40.662553

## 1. Images Processed
* **TrashNet**: 2115 images processed (2 duplicates, 0 corrupted).
* **RealWaste**: 2797 images processed (0 duplicates, 0 corrupted).
* **E-waste**: 747 valid crops extracted from 2157 images.
* **ConMetal-6**: 2488 evaluation crops extracted from 232 images. (Strictly placed in TEST split, NO training data).

## 2. Counts per Target Class
| Class | Train | Val | Test | Total |
|-------|-------|-----|------|-------|
| Plastic | 993 | 209 | 201 | 1403 |
| Aluminum | 0 | 0 | 384 | 384 |
| Copper | 0 | 0 | 398 | 398 |
| Steel | 0 | 0 | 1706 | 1706 |
| Paper | 769 | 156 | 169 | 1094 |
| Glass | 638 | 147 | 134 | 919 |
| Textile | 0 | 0 | 0 | 0 |
| E-waste | 511 | 119 | 117 | 747 |
| Cardboard | 594 | 127 | 143 | 864 |
| Other | 443 | 97 | 92 | 632 |

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
