import os
import time
import tensorflow as tf
import numpy as np
from api.src.kafkaOption.producer import sendData



def load_dataset(dataset):
    if dataset == "fashion_mnist":
        cache_path = "/app/datasets/fashion_mnist/"
        x_train = np.load( cache_path + "x_train.npy")
        y_train = np.load( cache_path + "y_train.npy")
        x_test  = np.load( cache_path + "x_test.npy")
        y_test  = np.load( cache_path + "y_test.npy")
        num_classes = 10

    elif dataset == "cifar100":
        cache_path = "/app/datasets/cifar100/"
        x_train = np.load( cache_path + "x_train.npy")
        y_train = np.load( cache_path + "y_train.npy")
        x_test  = np.load( cache_path + "x_test.npy")
        y_test  = np.load( cache_path + "y_test.npy")
        num_classes = 100

    else:
        raise ValueError("dataset inconnu")

    return x_train, y_train, x_test, y_test, num_classes


def train_tensorflow(dataset, epochs=15, cpu_samples = [], ram_samples = []):
    import psutil
    x_train, y_train, x_test, y_test, num_classes = load_dataset(dataset)

    model = tf.keras.Sequential([
        tf.keras.layers.Dense(num_classes)
    ])

    model.compile(
        optimizer="sgd",
        loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
        metrics=["accuracy"]
    )

    proc = psutil.Process()
    num_cpus = os.cpu_count() or 1
    start = time.time()
    history = []

    for epoch in range(epochs):
        cpu_time_start = time.thread_time()
        wall_start = time.time()
        ram_before = proc.memory_info().rss / (1024 ** 3)

        hist = model.fit(
            x_train,
            y_train,
            epochs=1,
            batch_size=64,
            verbose=0
        )

        loss, accuracy = model.evaluate(x_test, y_test, verbose=0)
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
            "loss": float(hist.history["loss"][0]),
            "accuracy": float(accuracy),
            "elapsed_time": time.time() - start
        }

        stats = {
            "cpu_avg": epoch_cpu_pct,
            "cpu_max": epoch_cpu_pct,
            "ram_avg_gb": epoch_ram_gb,
            "ram_max_gb": epoch_ram_gb,
        }

        sendData(point | stats, "tensorflow")

        history.append(point | stats)

        
    return {
        "library": "tensorflow",
        "dataset": dataset,
        "accuracy": history[-1]["accuracy"],
        "training_time": time.time() - start,
        "history": history
    }