import os
import json
import argparse
import torch
from torchvision import transforms, models
from PIL import Image

def predict(image_path, model_path, metadata_path):
    if not os.path.exists(model_path) or not os.path.exists(metadata_path):
        print(f"Error: Model or metadata not found.")
        return
        
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
        
    class_names = metadata['class_names']
    num_classes = metadata['num_classes']
    image_size = metadata.get('image_size', 224)
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    model = models.mobilenet_v2()
    model.classifier[1] = torch.nn.Linear(model.last_channel, num_classes)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model = model.to(device)
    model.eval()
    
    transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(image_size),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    
    try:
        image = Image.open(image_path).convert('RGB')
    except Exception as e:
        print(f"Error loading image: {e}")
        return
        
    input_tensor = transform(image).unsqueeze(0).to(device)
    
    with torch.no_grad():
        outputs = model(input_tensor)
        probabilities = torch.nn.functional.softmax(outputs[0], dim=0)
        
    probs, indices = torch.sort(probabilities, descending=True)
    
    print("\n--- INFERENCE RESULT ---")
    print("WARNING: This is a 7-class prototype. Aluminum, Copper, and Steel are excluded.\n")
    
    print(f"Predicted material: {class_names[indices[0].item()]}")
    print(f"Confidence: {probs[0].item():.4f}\n")
    
    print("Top 3:")
    for i in range(min(3, len(class_names))):
        print(f"{i+1}. {class_names[indices[i].item()]} - {probs[i].item():.4f}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('image_path', type=str, help='Path to the image to classify')
    parser.add_argument('--model-path', type=str, default='ml/models/material_classifier_mobilenetv2_7class.pth')
    parser.add_argument('--metadata-path', type=str, default='ml/models/material_classifier_7class_metadata.json')
    
    args = parser.parse_args()
    predict(args.image_path, args.model_path, args.metadata_path)
