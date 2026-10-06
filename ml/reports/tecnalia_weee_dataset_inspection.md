# TECNALIA WEEE Dataset Inspection Report

## 1. Dataset Structure and File Formats
The dataset is structured into two main folders:
*   `data/`: Contains the actual dataset files. For each capture, there are three files:
    *   `XXXX.mat`: A MATLAB file containing the raw hyperspectral data cube and band references.
    *   `XXXX.png`: An RGB representation of the hyperspectral image.
    *   `XXXX_gt.png`: A pixel-wise semantic segmentation ground truth mask.
*   `gt_source/`: Contains the original layered image editing files (13 files total, mix of Adobe Photoshop `.psd` and Paint.NET `.pdn` formats) used to create the ground truth masks.

## 2. Total Number of Images and Data Files
*   **Total files in `data/`:** 39 files.
*   **Total unique captures:** 13 sets.
*   This means there are exactly **13 RGB images** and **13 ground truth mask images** available in this dataset.

## 3. Available Material Classes and Label Mappings
The ground truth images (`_gt.png`) use specific pixel intensity values (0-6) to represent material classes:
*   `0`: Background
*   `1`: Copper
*   `2`: Brass
*   `3`: Aluminum
*   `4`: Lead (Not present in this dataset)
*   `5`: Stainless Steel
*   `6`: White_Copper

## 4. Explicit Labels for Aluminum, Copper, and Steel
Yes, the required target classes are explicitly labeled in this dataset:
*   **Aluminum:** Labeled as class index `3`.
*   **Copper:** Labeled as class index `1`.
*   **Steel:** Labeled as "Stainless Steel", class index `5`.

## 5. RGB Image Availability and MobileNetV2 Suitability
*   **Availability:** Yes, standard RGB images (`.png`) are provided for each of the 13 captures.
*   **Suitability for MobileNetV2:** **Low/Requires Heavy Preprocessing**. 
    *   **Format mismatch:** MobileNetV2 requires single-object image classification crops (e.g., one image = one label). This dataset provides multi-object *semantic segmentation* images (multiple pieces of scrap in a single frame). 
    *   **Data quantity:** With only 13 total images, the visual diversity (lighting, background, camera angles) is extremely limited. Even if hundreds of small crops are extracted from these 13 images, the model may overfit to the specific lighting conditions of the TECNALIA lab setup.

## 6. Ground-Truth to Image Correspondence
Ground truth is provided as pixel-wise semantic segmentation masks (`XXXX_gt.png`). Every pixel in the RGB image has a corresponding pixel in the `_gt.png` file, whose grayscale value (0 to 6) dictates the material class of that specific pixel. 

## 7. Dataset License and Academic Use
The `readme.md` does not explicitly declare a standardized open-source license (such as MIT or Creative Commons). However, it explicitly provides citation formats (`BibTeX`) for academic use, requesting that users cite their 2024 arXiv preprint and original 2010/2012 papers. 

## 8. Safety and Feasibility for Supplementing Current Dataset
**Feasibility:** Using this dataset to supplement the missing Aluminum, Copper, and Steel classes is technically possible but **highly complex**.
*   **Preprocessing Blocker:** You cannot simply copy these images into your training folders. You would need to write a script to find connected components (blobs) in the `_gt.png` masks, calculate bounding boxes around individual pieces of scrap, and crop the RGB images into hundreds of tiny, individual material images.
*   **Diversity Risk:** The resulting crops will all share the exact same background (the conveyor belt/surface used by TECNALIA) and lighting. 
*   **Recommendation:** While safe to use academically (with citation), it is not a drop-in replacement for standard classification datasets. It is highly recommended to prioritize obtaining the full **ConMetal-6** dataset, which is already formatted as bounding boxes (YOLO) and contains thousands of diverse, in-the-wild images.
