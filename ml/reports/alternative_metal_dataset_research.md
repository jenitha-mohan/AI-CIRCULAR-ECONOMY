# STEP 3E.5 — Alternative Metal Image Dataset Research

This report summarizes research into publicly available datasets to supply training and validation images for **Aluminum, Copper, and Steel**. 

The goal is to find real-world RGB images suitable for a MobileNetV2 classifier in the AI Circular Economy Marketplace, ensuring high visual diversity, explicit labeling, and safe commercial/academic licensing.

---

## 1. Candidate Datasets Comparison

| Dataset Name | Source | Potential Classes | Format | Visual Diversity | License / Access | Suitability |
|---|---|---|---|---|---|---|
| **ConMetal-6 (Full)** | Monash Univ. (Direct Request) | Aluminum, Copper, Steel | RGB Images + YOLO BBoxes | **High:** In-the-wild CDW conditions | CC BY 4.0 (Requires email request) | **High:** Perfectly matches project requirements. |
| **SteelDS** | Zenodo | Steel, Copper | RGB Video/Images + Masks | **Medium:** Simulated conveyor belt | Open (Exact CC variant TBC). Direct download. | **Medium:** Backgrounds are fixed (conveyor belt). |
| **Roboflow Universe Collections** | Roboflow | Varies (Needs verification) | RGB Images + BBoxes | **High:** Web-scraped / user-uploaded | Varies (CC BY common, but provenance risky) | **Low/Medium:** Requires manual relabeling. |
| **Mendeley Metal Spectral Data** | Mendeley Data | Aluminum, Copper, Steel | Spectrometer Data (1D/Hyperspectral) | N/A (Not standard RGB) | Open | **Unsuitable:** Not RGB images. |
| **Kaggle Surface Defects** | Kaggle | Aluminum, Steel | RGB Images (Microscopic/Texture) | **Low:** Extreme close-ups | Varies | **Unsuitable:** Focuses on scratches/defects, not scrap objects. |

---

## 2. Detailed Dataset Profiles

### A. ConMetal-6 (Complete Training Split)
*   **Source URL:** https://data.mendeley.com/datasets/ch34f38kz5/1 (Subset link; full dataset requires email to authors).
*   **Image Count:** 2,304 full images (35,787 annotated instances).
*   **Target Classes:** Explicitly labels `Aluminium`, `Copper`, `Galvanized Steel`, and `Stainless Steel`. (Generic `Ferrous Metal` and `Brass` can be excluded).
*   **Diversity & Independence:** Images captured "in-the-wild" with varying illumination and backgrounds. Pre-defined training/validation splits ensure no data leakage.
*   **License & Access:** CC BY 4.0. Academic and commercial use permitted with citation. Access requires manual email request to Monash University researchers.

### B. SteelDS (E40 Steel and Copper Scrap)
*   **Source URL:** [Zenodo - SteelDS](https://zenodo.org/search?q=%22SteelDS%22)
*   **Image Count:** High-resolution video frames and extracted images.
*   **Target Classes:** Shredded E40-grade Steel and Copper scrap. (Aluminum is *not* explicitly mentioned).
*   **Diversity & Independence:** **Data Leakage Risk.** Because the data is extracted from continuous video on a conveyor belt, adjacent frames contain the exact same physical objects. To avoid data leakage, splits must be created by separating independent video segments, not by randomly splitting frames. The background is uniform.
*   **License & Access:** Publicly hosted on Zenodo. Datasets here generally use CC BY or CC0, but specific commercial restrictions must be verified on the exact repository page.

### C. Roboflow Universe (Community Scrap Datasets)
*   **Source URL:** [Roboflow Universe - Scrap Metal](https://universe.roboflow.com/search?q=scrap%20metal)
*   **Target Classes:** Varies wildly. Users often upload custom datasets for "metal classification" or "rebar detection." 
*   **Diversity & Independence:** High diversity (often scraped from Google Images). Independence is usually maintained if images are unique.
*   **License & Access:** Users often tag these as CC BY 4.0 or MIT. **Warning:** Community-uploaded datasets often scrape copyrighted images from the web without permission. Using these in a commercial marketplace carries copyright risk despite the uploader's license tag. Classes are often lazily labeled (e.g., all white metal labeled "Aluminum" without verification).

### D. Mendeley / Kaggle (Surface Defects & Spectral)
*   *Mendeley "A Spectral Dataset of different materials... (2024)"* provides spectral curves (non-RGB), rendering it useless for MobileNetV2.
*   *Kaggle "Aluminum Profile Surface Defects" / "Severstal Steel"* provides extreme macroscopic close-ups of metal textures (cracks, pitting). These do not represent what a seller would upload (a photo of a metal can or pipe) and are therefore unusable for this project.

---

## 3. Recommendation for Next Data Acquisition Step

Based on this verified research, compiling random community datasets or using video-based datasets with fixed backgrounds (SteelDS) will likely introduce data leakage, overfitting, or licensing risks.

**Recommended Next Step:**
Do not compromise the dataset's integrity with unverified or unsuitable data. The **ConMetal-6 Full Dataset** remains the only rigorously verified, safely licensed, and highly diverse dataset that explicitly labels Aluminum, Copper, and Steel scrap in real-world RGB environments. 

You should **pause model training** and execute the manual request protocol (email the Monash University authors) to obtain the full ConMetal-6 training and validation splits.
