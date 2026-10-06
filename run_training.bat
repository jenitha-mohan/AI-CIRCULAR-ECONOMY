@echo off
echo ============================================
echo  MobileNetV2 7-Class Material Classifier
echo  3-Epoch Training Run
echo ============================================
python ml\training\train_material_classifier.py ^
  --epochs 3 ^
  --batch-size 32 ^
  --learning-rate 0.0001 ^
  --image-size 224 ^
  --seed 42 ^
  --num-workers 0 ^
  --model-path ml/models/material_classifier_mobilenetv2_7class.pth ^
  --metadata-path ml/models/material_classifier_7class_metadata.json ^
  --report-path ml/reports/material_classifier_7class_training_report.md
echo.
echo ============================================
echo  Training complete. Press any key to close.
echo ============================================
pause
