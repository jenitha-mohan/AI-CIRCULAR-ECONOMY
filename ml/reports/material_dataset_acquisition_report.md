# STEP 3E - Material Dataset Acquisition Report

## 1. Sources Investigated
*   **ConMetal-6 (Full Dataset)**
*   **RealWaste (Textile Trash)**

## 2. Sources Successfully Acquired
**NONE.** Both datasets require manual downloading and acceptance of terms/licenses via their respective web portals. Automated scraping or unauthenticated direct downloading was strictly avoided to comply with ethical sourcing rules.

## 3. Official Source URLs
*   **ConMetal-6**: https://data.mendeley.com/datasets/ch34f38kz5/1
*   **RealWaste**: https://archive.ics.uci.edu/dataset/908/realwaste (or via original GitHub mirror)

## 4. License
*   **ConMetal-6**: CC BY 4.0 (requires manual click-through verification)
*   **RealWaste**: CC BY 4.0

## 5. Original Dataset Size
*   **ConMetal-6**: ~2,304 images / 35,787 instances
*   **RealWaste (Textile Trash)**: ~318 images (based on historical counts of RealWaste dataset size)

## 6. Downloaded Dataset Size
**0 images.**

## 7. Aluminum Count (Newly Acquired)
0 (Train: 0)

## 8. Copper Count (Newly Acquired)
0 (Train: 0)

## 9. Steel Count (Newly Acquired)
0 (Train: 0)

## 10. Textile Count (Newly Acquired)
0 (Train: 0)

## 11. Train/Validation/Test Counts
No new images were added to the training, validation, or test splits.

## 12. Duplicate Removals
0

## 13. Corrupted Files
0

## 14. Rejected Crops
0

## 15. Excluded Classes
*   **ConMetal-6**: `Brass`, `Ferrous Metal`
*   **RealWaste**: `Metal`, `Food Waste`, `Vegetation`

## 16. Mapping Rules
*   `Aluminium` → `Aluminum`
*   `Galvanized Steel` → `Steel`
*   `Stainless Steel` → `Steel`
*   `Copper` → `Copper`
*   `Textile Trash` → `Textile`

## 17. Data Leakage Prevention Method
*   No training data was generated because the full datasets were not obtained.
*   The existing 232-image ConMetal-6 evaluation subset was strictly excluded from training.
*   No synthetic or duplicate images were generated to falsely pad the classes.

## 18. Remaining Problems
**MISSING TRAINING SOURCE**. Legitimate, licensed training data for Aluminum, Copper, Steel, and Textile is still missing because the source datasets must be manually downloaded by the user.
