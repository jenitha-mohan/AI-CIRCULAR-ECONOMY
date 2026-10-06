# STEP 3E.3 — TECNALIA Mask-to-Crop Feasibility Analysis

## 1. Inspection of RGB Images and Ground-Truth Masks
The dataset consists of 13 captures, each providing a hyperspectral `.mat` file, an RGB `.png` representation, and a semantic segmentation ground-truth mask `_gt.png`. The images depict multiple scattered pieces of Waste Electrical and Electronic Equipment (WEEE) scrap on a uniform background (likely a conveyor belt).

## 2. Material Label to Mask Pixel Mapping
Based on the `readme.md` and mask analysis, the pixel values map as follows:
*   `0`: Background
*   `1`: Copper
*   `2`: Brass
*   `3`: Aluminum
*   `5`: Stainless Steel
*   `6`: White_Copper

## 3. Distinct Labeled Objects
Using a connected components analysis script (`ml/training/analyze_tecnalia_crops.py`), the total number of distinct objects for the target classes are:
*   **Aluminum:** 240 distinct objects
*   **Stainless Steel:** 156 distinct objects
*   **Copper:** 62 distinct objects

## 4. Estimated Bounding Boxes and Dimensions
The objects range wildly in size, from tiny fragments to large pieces.
*   **Aluminum:** Width 1 - 359 px, Height 1 - 537 px
*   **Stainless Steel:** Width 1 - 300 px, Height 1 - 470 px
*   **Copper:** Width 2 - 328 px, Height 3 - 267 px

## 5. Small, Overlapping, and Unsuitable Crops
Many of the connected components are tiny fragments or noise. Using a minimum threshold of 30x30 pixels to define a "usable" crop for classification:
*   **Aluminum:** 81 objects are too small (< 30px)
*   **Stainless Steel:** 81 objects are too small (< 30px)
*   **Copper:** 10 objects are too small (< 30px)

Furthermore, because the images show scattered debris, bounding boxes around irregularly shaped objects will inevitably include pieces of neighboring objects. This overlap makes tight bounding box crops messy and potentially confusing for an image classifier expecting a single isolated object.

## 6. Context Suitability for Image Classification
An image classifier like MobileNetV2 relies on the context around the object. 
*   If we crop the RGB image using the bounding boxes, the background will be exactly the same uniform conveyor belt for every single crop.
*   The lack of diverse backgrounds (no hands, tables, outdoor lighting, varied surfaces) means a model trained on these crops would likely overfit to the specific lighting and background color of the TECNALIA lab setup, failing to generalize to user-uploaded photos in the Circular Economy Marketplace.

## 7. Data Leakage Risk
**Severe Risk.** 
There are 159 usable Aluminum crops coming from only 13 source images. This means dozens of crops come from the exact same capture. 
If these crops are randomly split into Training and Validation sets, crops from the *same original image* will exist in both sets. The validation set will share the exact same lighting, camera angle, and background as the training set, causing data leakage. The model will appear to have high accuracy, but it will be a false metric because it memorized the image conditions, not the material features.

## 8. Summary of Usable Crops
After filtering out fragments smaller than 30x30 pixels:
*   **Aluminum:** ~159 usable crops
*   **Stainless Steel:** ~75 usable crops
*   **Copper:** ~52 usable crops

## 9. License and Reuse Restrictions
**WARNING:** The `readme.md` file *does not* explicitly declare an open-source license (such as MIT, Apache, or Creative Commons). It only provides BibTeX citations for academic papers. 
*   Citation alone does not legally grant permission to redistribute, modify, or use the images in a commercial or public-facing application.
*   Without an explicit license, using this data in the AI Circular Economy Marketplace poses a copyright risk.

---

## Conclusion and Feasibility Summary

**Technical Feasibility:** 
Extraction is technically feasible using connected components to generate bounding boxes.

**Suitability as Supplementary Training Data:** 
**NOT SUITABLE.** 
1.  **Low Diversity:** All crops originate from only 13 uniform images, leading to extreme overfitting.
2.  **Data Leakage:** Splitting crops from the same 13 images into train/val will invalidate training metrics.
3.  **Context Issues:** Bounding boxes will capture overlapping debris.
4.  **Licensing:** Lack of an explicit open license makes redistribution risky.

**Recommendation:** Do not use this dataset to supplement the missing metals. Wait to obtain the complete, properly formatted, and explicitly licensed **ConMetal-6** dataset.
