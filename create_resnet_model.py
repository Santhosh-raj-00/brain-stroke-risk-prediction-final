import torch
import torchvision.models as models
import torch.nn as nn
import os

# Create the ResNet18 model with 2 classes as specified in the training script
model = models.resnet18(pretrained=True)

# Freeze early layers (as in the training script)
for param in model.parameters():
    param.requires_grad = False

# Replace the final layer to predict 2 classes (Normal vs Stroke)
num_ftrs = model.fc.in_features
model.fc = nn.Linear(num_ftrs, 2) 

# Create the dl_models directory if it doesn't exist
os.makedirs('dl_models', exist_ok=True)

# Save the model architecture (not trained, but with correct structure)
torch.save(model.state_dict(), 'dl_models/brain_stroke_cnn.pt')

print("Dummy ResNet18 model with 2-class output created successfully!")

# Also create the full model (architecture + weights)
model_full = models.resnet18(pretrained=True)
for param in model_full.parameters():
    param.requires_grad = False
num_ftrs_full = model_full.fc.in_features
model_full.fc = nn.Linear(num_ftrs_full, 2)

torch.save(model_full, 'dl_models/brain_stroke_cnn.pt')
print("Full ResNet18 model saved successfully!")