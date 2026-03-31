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


def train_pytorch(dataset, epochs=15, cpu_samples = [], ram_samples = []):
    import psutil, os
    train_dataset, test_dataset, input_size, num_classes = load_dataset(dataset)

    train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=64)

    model = Model(input_size, num_classes)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(model.parameters(), lr=0.01)

    proc = psutil.Process()
    num_cpus = os.cpu_count() or 1
    start = time.time()
    history = []

    
    for epoch in range(epochs):
        epoch_loss = 0.0
        cpu_time_start = time.thread_time()
        wall_start = time.time()
        ram_before = proc.memory_info().rss / (1024 ** 3)

        for images, labels in train_loader:
            outputs = model(images)
            loss = criterion(outputs, labels)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            epoch_loss += loss.item()

        accuracy = evaluate_model(model, test_loader)
        elapsed_time = time.time() - start

        cpu_time_end = time.thread_time()
        wall_end = time.time()
        ram_after = proc.memory_info().rss / (1024 ** 3)
        wall_delta = wall_end - wall_start
        cpu_delta = cpu_time_end - cpu_time_start
        epoch_cpu_pct = round((cpu_delta / wall_delta) * 100 / num_cpus, 2) if wall_delta > 0 else 0
        epoch_ram_gb = round((ram_before + ram_after) / 2, 2)

        cpu_samples.append(epoch_cpu_pct)
        ram_samples.append(epoch_ram_gb)

        point = {
            "epoch": epoch + 1,
            "loss": epoch_loss / len(train_loader),
            "accuracy": accuracy,
            "elapsed_time": elapsed_time,
        }

        stats = {
            "cpu_avg": epoch_cpu_pct,
            "cpu_max": epoch_cpu_pct,
            "ram_avg_gb": epoch_ram_gb,
            "ram_max_gb": epoch_ram_gb,
        }
        sendData(point | stats, "pytorch")

        history.append(point | stats)

    
    return {
        "library": "pytorch",
        "dataset": dataset,
        "accuracy": history[-1]["accuracy"],
        "training_time": time.time() - start,
        "history": history
    }