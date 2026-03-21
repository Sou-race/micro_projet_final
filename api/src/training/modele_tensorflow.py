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
    x_train, y_train, x_test, y_test, num_classes = load_dataset(dataset)

    model = tf.keras.Sequential([
        tf.keras.layers.Dense(num_classes)
    ])

    model.compile(
        optimizer="sgd",
        loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
        metrics=["accuracy"]
    )

    start = time.time()
    history = []

    for epoch in range(epochs):
        hist = model.fit(
            x_train,
            y_train,
            epochs=1,
            batch_size=64,
            verbose=0
        )

        loss, accuracy = model.evaluate(x_test, y_test, verbose=0)

        point = {
            "epoch": epoch + 1,
            "loss": float(hist.history["loss"][0]),
            "accuracy": float(accuracy),
            "elapsed_time": time.time() - start
        }

        stats = {
            "cpu_avg": round(sum(cpu_samples) / len(cpu_samples), 2) if cpu_samples else 0,
            "cpu_max": round(max(cpu_samples), 2) if cpu_samples else 0,
            "ram_avg_gb": round(sum(ram_samples) / len(ram_samples), 2) if ram_samples else 0,
            "ram_max_gb": round(max(ram_samples), 2) if ram_samples else 0,
        }

        sendData(point | stats, "tensorflow")
        #if progress_callback:
        #    progress_callback("tensorflow", point | stats)

        history.append(point)

        
    return {
        "library": "tensorflow",
        "dataset": dataset,
        "accuracy": history[-1]["accuracy"],
        "training_time": time.time() - start,
        "history": history
    }