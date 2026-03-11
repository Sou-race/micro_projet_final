from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.src.training.datasets.download_datasets import download_and_cache
from api.src.ressource.ressource import router
from bdd.database import Base, engine
import tensorflow as tf

Base.metadata.create_all(bind=engine)
app = FastAPI(title="microservice projet")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://happygood0.github.io",
        "http://localhost:5173",
        "http://localhost",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router)

download_and_cache("fashion_mnist", tf.keras.datasets.fashion_mnist.load_data, 10,  28*28)
download_and_cache("cifar100",      tf.keras.datasets.cifar100.load_data,      100, 32*32*3)


