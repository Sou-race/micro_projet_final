import time
import tensorflow as tf


def load_dataset(dataset):
    if dataset == "fashion_mnist":
        (x_train, y_train), (x_test, y_test) = tf.keras.datasets.fashion_mnist.load_data()

        x_train = x_train / 255.0
        x_test = x_test / 255.0

        x_train = x_train.reshape(-1, 28 * 28)
        x_test = x_test.reshape(-1, 28 * 28)

        num_classes = 10

    elif dataset == "cifar100":
        (x_train, y_train), (x_test, y_test) = tf.keras.datasets.cifar100.load_data()

        x_train = x_train / 255.0
        x_test = x_test / 255.0

        x_train = x_train.reshape(-1, 32 * 32 * 3)
        x_test = x_test.reshape(-1, 32 * 32 * 3)

        num_classes = 100

    else:
        raise ValueError("dataset inconnu")

    return x_train, y_train, x_test, y_test, num_classes


def train_tensorflow(dataset, epochs=15, progress_callback = None, cpu_samples = [], ram_samples = []):
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

        if progress_callback:
            progress_callback("tensorflow", point | stats)
        history.append(point)

    return {
        "library": "tensorflow",
        "dataset": dataset,
        "accuracy": history[-1]["accuracy"],
        "training_time": time.time() - start,
        "history": history
    }