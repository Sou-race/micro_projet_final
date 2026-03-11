import os
import numpy as np
import tensorflow as tf
from pathlib import Path

DATASETS_DIR = "/app"

def download_and_cache(dataset_name, loader_fn, num_classes, shape):
    fichier = Path("cifar100")
    if not fichier.exists():
        cache_path = os.path.join(DATASETS_DIR, "datasets/" + dataset_name)
        print(f"Téléchargement de {dataset_name}...")
        (x_train, y_train), (x_test, y_test) = loader_fn()
        x_train = x_train / 255.0
        x_test  = x_test  / 255.0
        x_train = x_train.reshape(-1, shape)
        x_test  = x_test.reshape(-1, shape)

        np.save(os.path.join(cache_path, "x_train.npy"), x_train)
        np.save(os.path.join(cache_path, "y_train.npy"), y_train)
        np.save(os.path.join(cache_path, "x_test.npy"),  x_test)
        np.save(os.path.join(cache_path, "y_test.npy"),  y_test)
        np.save(os.path.join(cache_path, "num_classes.npy"), np.array(num_classes))
        print(f"✓ {dataset_name} sauvegardé dans {cache_path}/")


print("\nTous les datasets sont prêts !")