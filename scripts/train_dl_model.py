
import os
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader, random_split
from PIL import Image
import time
import copy

def train_dl_model(data_dir='data/mri_dataset'):
    """
    Train a ResNet model for Stroke Classification
    Expected Directory Structure:
    data/mri_dataset/
        Normal/
        Ischemic_Stroke/
        Hemorrhagic_Stroke/
    """
    
    print("="*60)
    print("TRAINING DL MODEL (ResNet18) ON MRI/CT SCANS")
    print("="*60)
    
    # Configuration
    BATCH_SIZE = 32
    NUM_EPOCHS = 10
    LEARNING_RATE = 0.001
    MODEL_DIR = 'dl_models'
    MODEL_PATH = os.path.join(MODEL_DIR, 'stroke_cnn.pth')
    
    # Create model directory
    os.makedirs(MODEL_DIR, exist_ok=True)
    
    # Device config
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # Data Transforms
    data_transforms = {
        'train': transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.RandomHorizontalFlip(),
            transforms.RandomRotation(10),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ]),
        'val': transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ]),
    }
    
    # Load Data
    if not os.path.exists(data_dir):
        print(f"[ERROR] Dataset not found at {data_dir}")
        print("Please download a Stroke MRI Dataset (e.g., from Kaggle) and organize it into class folders.")
        
        # Option to download pre-trained weights instead
        print("\n[INFO] Downloading generic pre-trained weights (ImageNet) for demonstration...")
        try:
            model = models.resnet18(pretrained=True)
            num_ftrs = model.fc.in_features
            model.fc = nn.Linear(num_ftrs, 3) # 3 Classes
            torch.save(model.state_dict(), MODEL_PATH)
            print(f"[OK] Saved initialized model to {MODEL_PATH}")
            return
        except Exception as e:
            print(f"Error downloading weights: {e}")
            return

    try:
        full_dataset = datasets.ImageFolder(data_dir, data_transforms['train'])
        class_names = full_dataset.classes
        print(f"Classes found: {class_names}")
        
        # Split Data
        train_size = int(0.8 * len(full_dataset))
        val_size = len(full_dataset) - train_size
        train_dataset, val_dataset = random_split(full_dataset, [train_size, val_size])
        
        # Apply correct transforms (hacky since random_split doesn't copy transforms)
        val_dataset.dataset.transform = data_transforms['val']
        
        dataloaders = {
            'train': DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True),
            'val': DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False)
        }
        dataset_sizes = {'train': train_size, 'val': val_size}
        
    except Exception as e:
        print(f"Error loading data: {e}")
        return

    # Model Setup
    model = models.resnet18(pretrained=True)
    num_ftrs = model.fc.in_features
    model.fc = nn.Linear(num_ftrs, len(class_names))
    model = model.to(device)
    
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(model.parameters(), lr=LEARNING_RATE, momentum=0.9)
    
    # Training Loop
    since = time.time()
    best_model_wts = copy.deepcopy(model.state_dict())
    best_acc = 0.0
    
    for epoch in range(NUM_EPOCHS):
        print(f'Epoch {epoch+1}/{NUM_EPOCHS}')
        print('-' * 10)
        
        for phase in ['train', 'val']:
            if phase == 'train':
                model.train()
            else:
                model.eval()
                
            running_loss = 0.0
            running_corrects = 0
            
            for inputs, labels in dataloaders[phase]:
                inputs = inputs.to(device)
                labels = labels.to(device)
                
                optimizer.zero_grad()
                
                with torch.set_grad_enabled(phase == 'train'):
                    outputs = model(inputs)
                    _, preds = torch.max(outputs, 1)
                    loss = criterion(outputs, labels)
                    
                    if phase == 'train':
                        loss.backward()
                        optimizer.step()
                
                running_loss += loss.item() * inputs.size(0)
                running_corrects += torch.sum(preds == labels.data)
                
            epoch_loss = running_loss / dataset_sizes[phase]
            epoch_acc = running_corrects.double() / dataset_sizes[phase]
            
            print(f'{phase} Loss: {epoch_loss:.4f} Acc: {epoch_acc:.4f}')
            
            if phase == 'val' and epoch_acc > best_acc:
                best_acc = epoch_acc
                best_model_wts = copy.deepcopy(model.state_dict())
                
        print()
        
    time_elapsed = time.time() - since
    print(f'Training complete in {time_elapsed // 60:.0f}m {time_elapsed % 60:.0f}s')
    print(f'Best val Acc: {best_acc:4f}')
    
    # Save Model
    model.load_state_dict(best_model_wts)
    torch.save(model.state_dict(), MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")

if __name__ == '__main__':
    train_dl_model()
