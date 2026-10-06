import os
import time
import argparse
import json
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
from torchvision import datasets, transforms, models
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix, classification_report
from datetime import datetime
import numpy as np

# Target 7 classes
TARGET_CLASSES = [
    "Plastic",
    "Paper",
    "Glass",
    "Textile",
    "E-waste",
    "Cardboard",
    "Other"
]

def check_leakage(train_dir, val_dir, test_dir):
    print("Checking for data leakage...")
    
    def get_files(d):
        files = set()
        for root, _, fnames in os.walk(d):
            for f in fnames:
                if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                    # Use basename as a simple check for leakage, though full path won't leak
                    # Wait, if paths are unique it's fine. 
                    # Real leakage check: check if the exact same file content/name is in multiple splits.
                    files.add(f)
        return files

    train_files = get_files(train_dir)
    val_files = get_files(val_dir)
    test_files = get_files(test_dir)
    
    leakage_train_val = train_files.intersection(val_files)
    leakage_train_test = train_files.intersection(test_files)
    leakage_val_test = val_files.intersection(test_files)
    
    print(f"Train/Val overlap: {len(leakage_train_val)}")
    print(f"Train/Test overlap: {len(leakage_train_test)}")
    print(f"Val/Test overlap: {len(leakage_val_test)}")
    
    if len(leakage_train_val) > 0 or len(leakage_train_test) > 0 or len(leakage_val_test) > 0:
        print("WARNING: Data leakage detected!")
    else:
        print("No filename leakage detected across splits.")

class TargetClassImageFolder(datasets.ImageFolder):
    def find_classes(self, directory):
        classes = sorted([d.name for d in os.scandir(directory) if d.is_dir() and d.name in TARGET_CLASSES])
        if not classes:
            raise FileNotFoundError(f"Couldn't find any target class folder in {directory}.")
        class_to_idx = {cls_name: i for i, cls_name in enumerate(classes)}
        return classes, class_to_idx

def get_class_weights(dataset):
    class_counts = np.zeros(len(TARGET_CLASSES))
    for _, target in dataset.samples:
        class_counts[target] += 1
    total = np.sum(class_counts)
    weights = total / (len(TARGET_CLASSES) * class_counts)
    return torch.FloatTensor(weights)

def train(args):
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    data_dir = args.data_dir
    train_dir = os.path.join(data_dir, 'train')
    val_dir = os.path.join(data_dir, 'val')
    test_dir = os.path.join(data_dir, 'test')
    
    check_leakage(train_dir, val_dir, test_dir)
    
    # Transforms
    train_transform = transforms.Compose([
        transforms.RandomResizedCrop(args.image_size),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(15),
        transforms.ColorJitter(brightness=0.1, contrast=0.1, saturation=0.1, hue=0.1),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    
    val_transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(args.image_size),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    
    # Load datasets
    train_dataset = TargetClassImageFolder(train_dir, transform=train_transform)
    val_dataset = TargetClassImageFolder(val_dir, transform=val_transform)
    test_dataset = TargetClassImageFolder(test_dir, transform=val_transform)
    
    print(f"Train samples: {len(train_dataset)}")
    print(f"Val samples: {len(val_dataset)}")
    print(f"Test samples: {len(test_dataset)}")
    
    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True, num_workers=args.num_workers)
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size, shuffle=False, num_workers=args.num_workers)
    test_loader = DataLoader(test_dataset, batch_size=args.batch_size, shuffle=False, num_workers=args.num_workers)
    
    class_weights = get_class_weights(train_dataset).to(device)
    print(f"Class weights: {class_weights}")
    
    class_names = train_dataset.classes
    print(f"Model classes: {class_names}")

    # Model
    model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.DEFAULT)
    model.classifier[1] = nn.Linear(model.last_channel, len(class_names))
    model = model.to(device)
    
    criterion = nn.CrossEntropyLoss(weight=class_weights)
    optimizer = optim.AdamW(model.parameters(), lr=args.learning_rate)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='max', factor=0.1, patience=3)
    
    best_val_acc = 0.0
    best_epoch = -1
    
    print("\nStarting training...")
    for epoch in range(args.epochs):
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0
        
        for inputs, labels in train_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item() * inputs.size(0)
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()
            
        train_loss = running_loss / total
        train_acc = correct / total
        
        # Validation
        model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0
        
        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs, labels = inputs.to(device), labels.to(device)
                outputs = model(inputs)
                loss = criterion(outputs, labels)
                
                val_loss += loss.item() * inputs.size(0)
                _, predicted = outputs.max(1)
                val_total += labels.size(0)
                val_correct += predicted.eq(labels).sum().item()
                
        val_loss = val_loss / val_total
        val_acc = val_correct / val_total
        
        print(f"Epoch {epoch+1}/{args.epochs} | Train Loss: {train_loss:.4f} Acc: {train_acc:.4f} | Val Loss: {val_loss:.4f} Acc: {val_acc:.4f}")
        
        scheduler.step(val_acc)
        
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            best_epoch = epoch + 1
            os.makedirs(os.path.dirname(args.model_path), exist_ok=True)
            torch.save(model.state_dict(), args.model_path)
            print("  -> Saved best model!")
            
    print("\nTraining complete.")
    print(f"Best Validation Accuracy: {best_val_acc:.4f} at epoch {best_epoch}")
    
    # Evaluate on test set
    print("\nEvaluating on Test set...")
    model.load_state_dict(torch.load(args.model_path))
    model.eval()
    
    all_preds = []
    all_labels = []
    
    with torch.no_grad():
        for inputs, labels in test_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)
            _, predicted = outputs.max(1)
            all_preds.extend(predicted.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            
    test_acc = accuracy_score(all_labels, all_preds)
    precision, recall, f1_macro, _ = precision_recall_fscore_support(all_labels, all_preds, average='macro', zero_division=0)
    _, _, f1_weighted, _ = precision_recall_fscore_support(all_labels, all_preds, average='weighted', zero_division=0)
    
    print(f"Test Accuracy: {test_acc:.4f}")
    print(f"Test Macro F1: {f1_macro:.4f}")
    print(f"Test Weighted F1: {f1_weighted:.4f}")
    
    report_dict = classification_report(all_labels, all_preds, target_names=class_names, output_dict=True, zero_division=0)
    report_str = classification_report(all_labels, all_preds, target_names=class_names, zero_division=0)
    conf_mat = confusion_matrix(all_labels, all_preds)
    
    # Save Metadata
    metadata = {
        "model_architecture": "MobileNetV2",
        "num_classes": len(class_names),
        "class_names": class_names,
        "image_size": args.image_size,
        "training_epochs": args.epochs,
        "best_epoch": best_epoch,
        "validation_accuracy": best_val_acc,
        "test_metrics": {
            "accuracy": test_acc,
            "macro_f1": f1_macro,
            "weighted_f1": f1_weighted
        },
        "training_timestamp": datetime.now().isoformat(),
        "dataset_path": args.data_dir,
        "random_seed": args.seed,
        "pytorch_version": torch.__version__,
        "device_used": str(device)
    }
    
    with open(args.metadata_path, 'w') as f:
        json.dump(metadata, f, indent=4)
        
    # Generate Training Report
    report_content = f"""# 7-Class Material Classifier Training Report

**Date:** {datetime.now().isoformat()}

**WARNING: PROTOTYPE ONLY**
This is a 7-class prototype. Aluminum, Copper, and Steel were excluded from training because the currently verified dataset contains no training or validation images for these classes.

## 1. Objective
Build a temporary 7-class MobileNetV2 prototype classifier using transfer learning, omitting classes that lack training data.

## 2. Dataset Used
Path: `{args.data_dir}`

## 3. Classes
{', '.join(TARGET_CLASSES)}

## 4. Dataset Counts
- Train: {len(train_dataset)}
- Validation: {len(val_dataset)}
- Test: {len(test_dataset)}

## 5. Model Architecture
MobileNetV2 (pretrained on ImageNet), final layer replaced for {len(TARGET_CLASSES)} classes.

## 6. Transfer-learning Approach
Fine-tuning the entire model starting from ImageNet weights, using AdamW optimizer with CrossEntropyLoss and class weighting.

## 7. Training Configuration
- Epochs: {args.epochs}
- Batch Size: {args.batch_size}
- Learning Rate: {args.learning_rate}
- Image Size: {args.image_size}x{args.image_size}
- Random Seed: {args.seed}
- Device: {device}

## 8. Training Results
Best Epoch: {best_epoch}

## 9. Validation Results
Best Validation Accuracy: {best_val_acc:.4f}

## 10. Test Results
- Accuracy: {test_acc:.4f}
- Macro F1: {f1_macro:.4f}
- Weighted F1: {f1_weighted:.4f}

## 11. Per-class Metrics
```
{report_str}
```

## 12. Confusion Matrix
```
{np.array2string(conf_mat)}
```

## 13. Limitations
This model cannot detect Aluminum, Copper, or Steel. It may misclassify these metals as other classes.

## 14. Why this is only a 7-class prototype
There was no validated, non-leaking, properly licensed training data available for Aluminum, Copper, and Steel during the dataset preparation phase.

## 15. What is required before final 10-class training
Obtain the full ConMetal-6 dataset to populate the train and validation sets for Aluminum, Copper, and Steel, then rebuild and retrain the final 10-class model.
"""
    os.makedirs(os.path.dirname(args.report_path), exist_ok=True)
    with open(args.report_path, 'w') as f:
        f.write(report_content)
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data-dir', type=str, default='datasets/material_images')
    parser.add_argument('--epochs', type=int, default=15)
    parser.add_argument('--batch-size', type=int, default=32)
    parser.add_argument('--learning-rate', type=float, default=0.0001)
    parser.add_argument('--image-size', type=int, default=224)
    parser.add_argument('--num-workers', type=int, default=0)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--model-path', type=str, default='ml/models/material_classifier_mobilenetv2_7class.pth')
    parser.add_argument('--metadata-path', type=str, default='ml/models/material_classifier_7class_metadata.json')
    parser.add_argument('--report-path', type=str, default='ml/reports/material_classifier_7class_training_report.md')
    
    args = parser.parse_args()
    train(args)
