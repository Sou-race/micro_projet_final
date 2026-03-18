import time
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader, TensorDataset
import numpy as np
from api.src.kafkaOption.producer import sendData

class Model(nn.Module):
    def __init__(self, input_size, num_classes):
        super().__init__()
        self.linear = nn.Linear(input_size, num_classes)

    def forward(self, x):
        x = x.view(x.size(0), -1)
        return self.linear(x)


def load_dataset(dataset):
    if dataset == "fashion_mnist":
        cache_path = "/app/datasets/fashion_mnist/"
        x_train = np.load( cache_path + "x_train.npy")
        y_train = np.load( cache_path + "y_train.npy")
        x_test  = np.load( cache_path + "x_test.npy")
        y_test  = np.load( cache_path + "y_test.npy")
        input_size  = 28 * 28
        num_classes = 10

    elif dataset == "cifar100":
        cache_path = "/app/datasets/cifar100/"
        x_train = np.load( cache_path + "x_train.npy")
        y_train = np.load( cache_path + "y_train.npy")
        x_test  = np.load( cache_path + "x_test.npy")
        y_test  = np.load( cache_path + "y_test.npy")
        input_size  = 32 * 32 * 3
        num_classes = 100

    else:
        raise ValueError("dataset inconnu")
    
    train_dataset = TensorDataset(
        torch.tensor(x_train, dtype=torch.float32),
        torch.tensor(y_train, dtype=torch.long).squeeze()
    )
    test_dataset = TensorDataset(
        torch.tensor(x_test, dtype=torch.float32),
        torch.tensor(y_test, dtype=torch.long).squeeze()
    )
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

    test = {
    "testid": "1",
    "teststr": "test"
    }
    
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

        sendData((test))
    return {
        "library": "pytorch",
        "dataset": dataset,
        "accuracy": history[-1]["accuracy"],
        "training_time": time.time() - start,
        "history": history
    }
