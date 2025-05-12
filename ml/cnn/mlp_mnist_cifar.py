import torch
from torch import nn, optim
from torch.utils.data import DataLoader, Subset
from torchvision import datasets, transforms
from sklearn.model_selection import KFold
import numpy as np
import time

transform_mnist = transforms.Compose([
    transforms.ToTensor()
])

transform_cifar = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
])

mnist_train = datasets.MNIST(root='./data', train=True, download=True, transform=transform_mnist)
mnist_test = datasets.MNIST(root='./data', train=False, download=True, transform=transform_mnist)

cifar_train = datasets.CIFAR10(root='./data', train=True, download=True, transform=transform_cifar)
cifar_test = datasets.CIFAR10(root='./data', train=False, download=True, transform=transform_cifar)

class MLP(nn.Module):
    def __init__(self, input_size, layer_sizes, output_size, dropout):
        super().__init__()
        layers = []
        prev = input_size
        for size in layer_sizes:
            layers.append(nn.Linear(prev, size))
            layers.append(nn.ReLU())
            if dropout > 0:
                layers.append(nn.Dropout(dropout))
            prev = size
        layers.append(nn.Linear(prev, output_size))
        self.net = nn.Sequential(*layers)

    def forward(self, x):
        x = x.view(x.size(0), -1)
        return self.net(x)

def train_model(model, loader, optimizer, criterion, device):
    model.train()
    total_loss = 0
    for x, y in loader:
        x, y = x.to(device), y.to(device)
        optimizer.zero_grad()
        loss = criterion(model(x), y)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
    return total_loss / len(loader)

def evaluate_model(model, loader, device):
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for x, y in loader:
            x, y = x.to(device), y.to(device)
            preds = model(x).argmax(dim=1)
            correct += (preds == y).sum().item()
            total += y.size(0)
    return correct / total

def run_cv(dataset, input_size, layer_sizes, output_size, search_space, folds=3, device='cpu'):
    kf = KFold(n_splits=folds, shuffle=True, random_state=0)
    indices = list(range(len(dataset)))
    results = []

    for config in search_space:
        acc_scores = []
        start_time = time.time()

        print(f"\n=== Config: {config}, Architecture: {layer_sizes} ===")

        for fold, (train_idx, val_idx) in enumerate(kf.split(indices)):
            print(f"\n--- Fold {fold + 1}/{folds} ---")
            
            train_data = Subset(dataset, train_idx)
            val_data = Subset(dataset, val_idx)

            train_loader = DataLoader(train_data, batch_size=config['batch_size'], shuffle=True)
            val_loader = DataLoader(val_data, batch_size=config['batch_size'], shuffle=False)

            model = MLP(input_size, layer_sizes, output_size, config['dropout']).to(device)
            optimizer = optim.SGD(model.parameters(), lr=config['lr']) if config['optimizer'] == 'SGD' \
                        else optim.Adam(model.parameters(), lr=config['lr'])
            criterion = nn.CrossEntropyLoss()

            for epoch in range(15):
                train_loss = train_model(model, train_loader, optimizer, criterion, device)
                val_acc = evaluate_model(model, val_loader, device)
                print(f"Epoch {epoch+1:02d}/15 - Train Loss: {train_loss:.4f} - Val Acc: {val_acc:.4f}")

            final_acc = evaluate_model(model, val_loader, device)
            acc_scores.append(final_acc)

        mean_acc = np.mean(acc_scores)
        std_acc = np.std(acc_scores)
        runtime = time.time() - start_time

        results.append({
            'architecture': layer_sizes,
            'config': config,
            'mean_acc': mean_acc,
            'std_acc': std_acc,
            'runtime_sec': runtime
        })

    return results

shallow = [128]
medium = [512, 256, 128]
deep = [4096, 2048, 1024, 512, 256, 128, 64]

search_space = [
    {'lr': 0.01, 'batch_size': 64, 'optimizer': 'SGD', 'dropout': 0.0},
    {'lr': 0.001, 'batch_size': 64, 'optimizer': 'Adam', 'dropout': 0.2},
    {'lr': 0.001, 'batch_size': 128, 'optimizer': 'Adam', 'dropout': 0.5}
]

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

#MNIST
input_mnist = 28 * 28
output_mnist = 10
mnist_results = []
for arch in [shallow, medium, deep]:
    mnist_results.extend(run_cv(mnist_train, input_mnist, arch, output_mnist, search_space, device=device))

#CIFAR-10
input_cifar = 3 * 32 * 32
output_cifar = 10
cifar_results = []
for arch in [shallow, medium, deep]:
    cifar_results.extend(run_cv(cifar_train, input_cifar, arch, output_cifar, search_space, device=device))

import pandas as pd

print("\nMNIST Results:")
mnist_df = pd.DataFrame(mnist_results)
print(mnist_df[['architecture', 'config', 'mean_acc', 'std_acc', 'runtime_sec']])

print("\nCIFAR-10 Results:")
cifar_df = pd.DataFrame(cifar_results)
print(cifar_df[['architecture', 'config', 'mean_acc', 'std_acc', 'runtime_sec']])
