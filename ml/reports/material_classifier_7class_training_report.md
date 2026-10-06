# 7-Class Material Classifier Training Report

**Date:** 2026-10-06T22:49:41.363758

**WARNING: PROTOTYPE ONLY**
This is a 7-class prototype. Aluminum, Copper, and Steel were excluded from training because the currently verified dataset contains no training or validation images for these classes.

## 1. Objective
Build a temporary 7-class MobileNetV2 prototype classifier using transfer learning, omitting classes that lack training data.

## 2. Dataset Used
Path: `datasets/material_images`

## 3. Classes
Plastic, Paper, Glass, Textile, E-waste, Cardboard, Other

## 4. Dataset Counts
- Train: 3831
- Validation: 902
- Test: 905

## 5. Model Architecture
MobileNetV2 (pretrained on ImageNet), final layer replaced for 7 classes.

## 6. Transfer-learning Approach
Fine-tuning the entire model starting from ImageNet weights, using AdamW optimizer with CrossEntropyLoss and class weighting.

## 7. Training Configuration
- Epochs: 3
- Batch Size: 32
- Learning Rate: 0.0001
- Image Size: 224x224
- Random Seed: 42
- Device: cpu

## 8. Training Results
Best Epoch: 3

## 9. Validation Results
Best Validation Accuracy: 0.8426

## 10. Test Results
- Accuracy: 0.8497
- Macro F1: 0.8537
- Weighted F1: 0.8491

## 11. Per-class Metrics
```
              precision    recall  f1-score   support

   Cardboard       0.92      0.76      0.83       143
     E-waste       1.00      0.99      1.00       117
       Glass       0.83      0.90      0.86       134
       Other       0.69      0.74      0.72        92
       Paper       0.81      0.92      0.86       169
     Plastic       0.85      0.77      0.80       201
     Textile       0.85      0.96      0.90        49

    accuracy                           0.85       905
   macro avg       0.85      0.86      0.85       905
weighted avg       0.85      0.85      0.85       905

```

## 12. Confusion Matrix
```
[[109   0   1   8  19   5   1]
 [  0 116   0   0   1   0   0]
 [  1   0 120   1   0  12   0]
 [  2   0   1  68   7   7   7]
 [  5   0   0   5 155   4   0]
 [  2   0  22  15   8 154   0]
 [  0   0   0   1   1   0  47]]
```

## 13. Limitations
This model cannot detect Aluminum, Copper, or Steel. It may misclassify these metals as other classes.

## 14. Why this is only a 7-class prototype
There was no validated, non-leaking, properly licensed training data available for Aluminum, Copper, and Steel during the dataset preparation phase.

## 15. What is required before final 10-class training
Obtain the full ConMetal-6 dataset to populate the train and validation sets for Aluminum, Copper, and Steel, then rebuild and retrain the final 10-class model.
