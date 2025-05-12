import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Subset
from torchvision import datasets, transforms
from sklearn.model_selection import KFold
import numpy as np
import pandas as pd
import time

transform_mnist = transforms.ToTensor()
transform_cifar = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.5,), (0.5,)) if datasets.CIFAR10 else transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
])

mnist_train = datasets.MNIST(root='./data', train=True, download=True, transform=transform_mnist)
mnist_test = datasets.MNIST(root='./data', train=False, download=True, transform=transform_mnist)
cifar_train = datasets.CIFAR10(root='./data', train=True, download=True, transform=transform_cifar)
cifar_test = datasets.CIFAR10(root='./data', train=False, download=True, transform=transform_cifar)

class CNNBaseline(nn.Module):
    def __init__(self, input_channels, num_classes, dropout=0.0):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(input_channels, 32, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2)
        )
        
        self.flatten_size = 64 * 7 * 7 if input_channels == 1 else 64 * 8 * 8
        
        self.classifier = nn.Sequential(
            nn.Linear(self.flatten_size, 128),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(128, num_classes)
        )

    def forward(self, x):
        x = self.features(x)
        x = x.view(x.size(0), -1)
        return self.classifier(x)

class CNNEnhanced(nn.Module):
    def __init__(self, input_channels, num_classes, dropout=0.5):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv2d(input_channels, 32, 3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Flatten(),
            nn.Dropout(dropout),
            nn.Linear(64 * 7 * 7 if input_channels == 1 else 64 * 8 * 8, num_classes)
        )

    def forward(self, x): return self.net(x)

class CNNDeep(nn.Module):
    def __init__(self, input_channels, num_classes, dropout=0.5):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv2d(input_channels, 32, 3, padding=1), nn.BatchNorm2d(32), nn.ReLU(),
            nn.Conv2d(32, 64, 3, padding=1), nn.BatchNorm2d(64), nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(64, 128, 3, padding=1), nn.BatchNorm2d(128), nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Flatten(),
            nn.Dropout(dropout),
            nn.Linear(128 * 7 * 7 if input_channels == 1 else 128 * 8 * 8, 256),
            nn.ReLU(),
            nn.Linear(256, num_classes)
        )

    def forward(self, x): return self.net(x)

def train_model(model, loader, optimizer, criterion, device):
    model.train()
    total_loss = 0
    for x, y in loader:
        x, y = x.to(device), y.to(device)
        optimizer.zero_grad()
        output = model(x)
        loss = criterion(output, y)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
    return total_loss / len(loader)

def evaluate_model(model, loader, device):
    model.eval()
    correct = total = 0
    with torch.no_grad():
        for x, y in loader:
            x, y = x.to(device), y.to(device)
            preds = model(x).argmax(dim=1)
            correct += (preds == y).sum().item()
            total += y.size(0)
    return correct / total


def run_cv(dataset, model_cls, model_args, search_space, input_shape, num_classes, folds=3, device='cpu'):
    kf = KFold(n_splits=folds, shuffle=True, random_state=0)
    indices = list(range(len(dataset)))
    results = []

    for config in search_space:
        acc_scores = []
        start_time = time.time()

        for fold, (train_idx, val_idx) in enumerate(kf.split(indices), 1):
            print(f"\n{'='*40}\nFold {fold} - Model: {model_cls.__name__} - Config: {config}\n{'='*40}")
            train_subset = Subset(dataset, train_idx)
            val_subset = Subset(dataset, val_idx)

            train_loader = DataLoader(train_subset, batch_size=config['batch_size'], shuffle=True)
            val_loader = DataLoader(val_subset, batch_size=config['batch_size'], shuffle=False)

            model = model_cls(*model_args, dropout=config['dropout']).to(device)
            optimizer = optim.SGD(model.parameters(), lr=config['lr']) if config['optimizer'] == 'SGD' else optim.Adam(model.parameters(), lr=config['lr'])
            criterion = nn.CrossEntropyLoss()

            for epoch in range(15):
                train_loss = train_model(model, train_loader, optimizer, criterion, device)
                val_acc = evaluate_model(model, val_loader, device)
                print(f"Epoch {epoch+1:02d}: Train Loss = {train_loss:.4f} | Val Acc = {val_acc:.4f}")

            acc_scores.append(val_acc)

        mean_acc = np.mean(acc_scores)
        std_acc = np.std(acc_scores)
        runtime = time.time() - start_time

        results.append({
            'model': model_cls.__name__,
            'config': config,
            'mean_acc': mean_acc,
            'std_acc': std_acc,
            'runtime_sec': runtime
        })

    return results

search_space = [
    {'lr': 0.01, 'batch_size': 64, 'optimizer': 'SGD', 'dropout': 0.0},
    {'lr': 0.001, 'batch_size': 64, 'optimizer': 'Adam', 'dropout': 0.25},
    {'lr': 0.001, 'batch_size': 128, 'optimizer': 'Adam', 'dropout': 0.5}
]

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


def run_experiments(train_data, input_channels, model_classes, output_classes, name):
    results = []
    for model_cls in model_classes:
        results.extend(run_cv(
            train_data, model_cls, (input_channels, output_classes), search_space,
            input_shape=(1, 28, 28) if input_channels == 1 else (3, 32, 32),
            num_classes=output_classes, device=device
        ))

    df = pd.DataFrame(results)
    print(f"\n{name} Results:")
    print(df[['model', 'config', 'mean_acc', 'std_acc', 'runtime_sec']])
    return df

mnist_df = run_experiments(mnist_train, input_channels=1, model_classes=[CNNBaseline, CNNEnhanced, CNNDeep], output_classes=10, name="MNIST")
cifar_df = run_experiments(cifar_train, input_channels=3, model_classes=[CNNBaseline, CNNEnhanced, CNNDeep], output_classes=10, name="CIFAR-10")
