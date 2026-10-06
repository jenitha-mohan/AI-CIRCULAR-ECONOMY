# Material Dataset Preparation Report — STEP 3E.1 (Textile Addition)

**Updated:** 2026-10-01T23:26:03.013463

## Textile Source Details
| Field | Value |
|---|---|
| Source dataset | RealWaste |
| Source URL | https://github.com/sam-single/realwaste |
| License | CC BY 4.0 |
| Original class name | Textile Trash |
| Target class | Textile |
| Source images | 318 |
| Valid images processed | 318 |
| Train added | 222 |
| Val added | 47 |
| Test added | 49 |
| Duplicates skipped | 0 |
| Corrupted skipped | 0 |
| Unsupported skipped | 0 |

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
| Plastic | 993 | 209 | 201 | 1403 |
| Aluminum | 0 | 0 | 384 | 384 |
| Copper | 0 | 0 | 398 | 398 |
| Steel | 0 | 0 | 1706 | 1706 |
| Paper | 769 | 156 | 169 | 1094 |
| Glass | 638 | 147 | 134 | 919 |
| Textile | 222 | 47 | 49 | 318 |
| E-waste | 511 | 119 | 117 | 747 |
| Cardboard | 594 | 127 | 143 | 864 |
| Other | 443 | 97 | 92 | 632 |

## MobileNetV2 Readiness
**NOT READY.** Aluminum, Copper, and Steel still have 0 training and validation images.
The ConMetal-6 evaluation images remain strictly in test only.
Model training must not begin until all 10 classes have training and validation data.
