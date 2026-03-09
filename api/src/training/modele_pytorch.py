import time
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader


class Model(nn.Module):
    def __init__(self, input_size, num_classes):
        super().__init__()
        self.linear = nn.Linear(input_size, num_classes)

    def forward(self, x):
        x = x.view(x.size(0), -1)
        return self.linear(x)


def load_dataset(dataset):
    transform = transforms.ToTensor()

    if dataset == "fashion_mnist":
        train_dataset = datasets.FashionMNIST(
            root="./data",
            train=True,
            download=True,
            transform=transform
        )
        test_dataset = datasets.FashionMNIST(
            root="./data",
            train=False,
            download=True,
            transform=transform
        )
        input_size = 28 * 28
        num_classes = 10

    elif dataset == "cifar100":
        train_dataset = datasets.CIFAR100(
            root="./data",
            train=True,
            download=True,
            transform=transform
        )
        test_dataset = datasets.CIFAR100(
            root="./data",
            train=False,
            download=True,
            transform=transform
        )
        input_size = 32 * 32 * 3
        num_classes = 100

    else:
        raise ValueError("dataset inconnu")

    return train_dataset, test_dataset, input_size, num_classes


def evaluate_model(model, test_loader):
    correct = 0
    total = 0

    with torch.no_grad():
        for images, labels in test_loader:
            outputs = model(images)
            _, predicted = torch.max(outputs, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

    return correct / total


def train_pytorch(dataset, epochs=15, progress_callback = None, cpu_samples = [], ram_samples = []):
    train_dataset, test_dataset, input_size, num_classes = load_dataset(dataset)

    train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=64)

    model = Model(input_size, num_classes)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(model.parameters(), lr=0.01)

    start = time.time()
    history = []

    for epoch in range(epochs):
        epoch_loss = 0.0

        for images, labels in train_loader:
            outputs = model(images)
            loss = criterion(outputs, labels)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            epoch_loss += loss.item()

        accuracy = evaluate_model(model, test_loader)
        epoch_time = time.time() - start

        point = {
            "epoch": epoch + 1,
            "loss": epoch_loss / len(train_loader),
            "accuracy": accuracy,
            "elapsed_time": epoch_time,
        }

        stats = {
            "cpu_avg": round(sum(cpu_samples) / len(cpu_samples), 2) if cpu_samples else 0,
            "cpu_max": round(max(cpu_samples), 2) if cpu_samples else 0,
            "ram_avg_gb": round(sum(ram_samples) / len(ram_samples), 2) if ram_samples else 0,
            "ram_max_gb": round(max(ram_samples), 2) if ram_samples else 0,
        }

        if progress_callback:
            progress_callback("pytorch", point | stats)
        history.append(point)

    return {
        "library": "pytorch",
        "dataset": dataset,
        "accuracy": history[-1]["accuracy"],
        "training_time": time.time() - start,
        "history": history
    }
