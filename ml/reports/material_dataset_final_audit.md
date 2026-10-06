# Final Safety Audit - Material Classification Dataset

## Audit Verification Checklist
*   [ ] Every target class has >0 training images *(FAILED: Aluminum, Copper, Steel, Textile have 0)*
*   [ ] Every target class has >0 validation images *(FAILED: Aluminum, Copper, Steel, Textile have 0)*
*   [ ] Every target class has >0 test images *(FAILED: Textile has 0)*
*   [x] No exact duplicate SHA-256 exists across train/val/test
*   [x] No ConMetal evaluation subset image has been placed into train
*   [x] No Brass exists in Steel
*   [x] No Ferrous Metal exists in Steel
*   [x] No generic Metal has been mapped to Aluminum/Copper/Steel
*   [x] No synthetic images exist
*   [x] No fabricated labels exist
*   [x] All images are readable
*   [x] All source licenses are recorded

## MISSING TRAINING SOURCE
The dataset is **INCOMPLETE**. The full ConMetal-6 dataset and the RealWaste Textile Trash subset could not be automatically downloaded due to licensing/authentication blockers. Therefore, no training data exists for Aluminum, Copper, Steel, or Textile.

## Final Dataset State

| Class | Train | Val | Test | Total |
|---|---|---|---|---|
| Plastic | 993 | 209 | 201 | 1403 |
| Aluminum | 0 | 0 | 384 | 384 |
| Copper | 0 | 0 | 398 | 398 |
| Steel | 0 | 0 | 1706 | 1706 |
| Paper | 769 | 156 | 169 | 1094 |
| Glass | 638 | 147 | 134 | 919 |
| Textile | 0 | 0 | 0 | 0 |
| E-waste | 511 | 119 | 117 | 747 |
| Cardboard | 594 | 127 | 143 | 864 |
| Other | 449 | 97 | 86 | 632 |

**Status:** DO NOT TRAIN MOBILENETV2.
