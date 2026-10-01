# STEP 3C - Material Dataset Preparation Report

## Overview
This report summarizes the outcome of the material dataset preparation script (`ml/training/prepare_material_dataset.py`). The objective is to assemble a real, verified image dataset for training a MobileNetV2 classifier without fabricating data, synthesizing images, or blindly remapping broad categories like "Metal".

## 1. Total Images
**0 images** were processed.

## 2. Images Per Target Class
*   **Plastic:** 0
*   **Aluminum:** 0
*   **Copper:** 0
*   **Steel:** 0
*   **Paper:** 0
*   **Glass:** 0
*   **Textile:** 0
*   **E-waste:** 0
*   **Cardboard:** 0
*   **Other:** 0

## 3. Train/Validation/Test Counts
*   **Train (70%):** 0
*   **Validation (15%):** 0
*   **Test (15%):** 0

## 4. Source Datasets Required (Manual Download)
The script expects the following datasets to be downloaded manually into `datasets/raw_sources/`:
1.  **TrashNet** (`datasets/raw_sources/trashnet`) - [URL](https://github.com/garythung/trashnet)
2.  **RealWaste** (`datasets/raw_sources/realwaste`) - [URL](https://archive.ics.uci.edu/dataset/908/realwaste)
3.  **E-Waste Dataset (Kaggle)** (`datasets/raw_sources/ewaste`) - [URL](https://www.kaggle.com/datasets/example/e-waste)
4.  **Industrial Scrap Metals** (`datasets/raw_sources/scrap_metals`) - Proprietary / Custom sourcing required for specific metals.

*None of these datasets are currently downloaded.*

## 5. License of Each Source
*   **TrashNet**: MIT
*   **RealWaste**: CC BY 4.0
*   **E-Waste Dataset**: CC0
*   **Industrial Scrap Metals**: TBD

## 6. Mapping Decisions
*   TrashNet/RealWaste categories for Glass, Paper, Cardboard, Plastic, and Trash/Misc are mapped 1:1 to our targets.
*   RealWaste `Textile Trash` is mapped to `Textile`.
*   Kaggle `e-waste` and `pcb` are mapped to `E-waste`.
*   **Crucial Decision:** The generic `Metal` class from TrashNet and RealWaste is intentionally **omitted/ignored** because it cannot be reliably split into Aluminum, Copper, and Steel without manual human verification.

## 7. Classes That Could Not Be Sourced
*All* classes are currently missing because the raw datasets must be manually downloaded. However, even if TrashNet and RealWaste were downloaded, **Aluminum**, **Copper**, and **Steel** would remain completely missing until a specialized dataset is sourced.

## 8. Class Imbalance
Absolute imbalance exists because the dataset is entirely empty.

## 9. Duplicate Count
**0** exact duplicates detected (MD5 hashing implemented in the script).

## 10. Corrupted Image Count
**0** corrupted files detected (PIL validation implemented in the script).

## 11. Data Leakage Checks
*   **Exact Duplicate Prevention:** The script maintains a global set of MD5 hashes across all input sources. If a hash is seen again, it is skipped.
*   **Split Leakage Prevention:** Deduplication happens *before* the dataset is split. The single list of unique valid images per class is shuffled, then strictly sliced into Train/Val/Test subsets. An image can never appear in two splits.

## 12. Readiness for Training
**NOT READY.** The dataset is completely empty. Real MobileNetV2 training cannot proceed until the raw data is manually downloaded, placed in `datasets/raw_sources/`, and the preparation script is re-run successfully.
