# ConMetal-6: Alloy-Level CDW Metal Detection Dataset (v1.0)

## Overview

This is the 10% of the **ConMetal-6** dataset, a fine-grained, alloy-level object detection dataset for construction and demolition waste (CDW) metal streams captured under in-the-wild conditions.

The complete ConMetal-6 dataset is available on request (see below).

## Dataset Summary

| Property                  | Value                                         |
|---------------------------|---------------------------------------------  |
| **Images**                | 232 RGB images (.jpg)                         |
| **Annotated instances**   | 4,620 bounding-box annotations                |
| **Number of classes**     | 6 metal alloy types                           |
| **Imaging conditions**    | In-the-wild (Varying illumination conditions) |
| **Capture location**      | Melbourne, Australia                          |
| **Annotation format**     | YOLO format (per-image .txt files)            |
| **Image source**          | Mobile RGB sensors                            |
| **Ground truth method**   | Magnetic testing, scratch testing, expert review |

## Class Definitions and Instance Counts

| Class ID | Class Name         | Instances in Test Set |
|----------|--------------------|-----------------------|
| 0        | Aluminium          | 400                   |
| 1        | Brass              | 897                   |
| 2        | Copper             | 412                   |
| 3        | Ferrous Metal      | 1,179                 |
| 4        | Galvanized Steel   | 246                   |
| 5        | Stainless Steel    | 1,486                 |
|          | **Total**          | **4,620**             |


## Dataset Structure

```
ConMetal-6-v1.0/
├── images/          # 232 images
├── labels/          # 232 annotation files
├── data.yaml
└── README.md

## Annotation Format

Annotations are provided in **YOLO format**. Each image has a corresponding `.txt` file in the `labels/` directory. Each line in a label file represents one annotated object with the following format:

## Full Dataset Access

This public subset represents the test split of ConMetal-6. The complete dataset comprises:
- **2,304 images** with **35,787 annotated instances** across six alloy classes.
- Training (70%), validation (20%), and test (10%) splits.

The complete dataset is available on request for research purposes. Please contact:
- **Mehrdad Arashpour (corresponding):** mehrdad.arashpour@monash.edu
- **Diyana Ranasinghe:** diyana.athidewaranasinghe@monash.edu

An expanded version of ConMetal-6, incorporating instance segmentation annotations and additional imaging modalities, is under active development and will be publicly released as a unified benchmark upon completion.

## Citation

If you use this dataset in your research, please cite:

Ranasinghe, Diyana; Arashpour, Mehrdad (2026), “ConMetal-6 subset”, Mendeley Data, V1, doi: 10.17632/ch34f38kz5.1


## Licence

This dataset is released under the [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/) licence.

You are free to share and adapt this dataset for any purpose, provided appropriate credit is given.

## Acknowledgements

The authors acknowledge support from the ASCII Lab (https://www.monash.edu/ascii) at Monash University, and the Civil Engineering and Mechanical and Aerospace Engineering labs for expert review during data curation.
