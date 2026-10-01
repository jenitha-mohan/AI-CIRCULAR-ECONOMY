# Real Material Dataset for AI Classification

This directory contains the REAL image dataset intended for training the MobileNetV2 AI material classification model.

## Folder Structure

The dataset is strictly organized into `train`, `val`, and `test` splits (70/15/15 ratio), and within each split, there are 10 target classes:

1. Plastic
2. Aluminum
3. Copper
4. Steel
5. Paper
6. Glass
7. Textile
8. E-waste
9. Cardboard
10. Other

## Label Mapping & Constraints

A major challenge with public waste datasets (like TrashNet or RealWaste) is that they often group all metals into a single `Metal` category. 

**Rule:** We DO NOT map a broad "Metal" class to Aluminum, Copper, or Steel arbitrarily. 

- **Glass, Paper, Cardboard, Plastic, Textile**: Can be sourced directly from datasets like TrashNet or RealWaste.
- **E-waste**: Must be sourced from specific E-waste datasets (e.g., from Kaggle).
- **Aluminum, Copper, Steel**: Must be sourced from specialized industrial scrap metal datasets, or the "Metal" images from broad datasets must be manually annotated and verified by human reviewers.
- **Other**: Used as a catch-all for miscellaneous trash or non-target items.

## Sourcing & Licensing

Refer to `dataset_manifest.json` for the full list of considered sources, their URLs, and licensing (e.g., MIT, CC BY 4.0).

## Current Status

Currently, the dataset folders are **empty**. A real dataset MUST be assembled, verified, and placed into these folders before any model training can occur. We do not fabricate data or duplicate images artificially.

## Running the Audit

To check the status of the dataset, run the audit script:

```bash
python ml/training/audit_material_dataset.py
```

This script will report class distributions, detect corrupted files, and identify exact duplicate images.
