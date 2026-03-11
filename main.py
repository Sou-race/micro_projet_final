import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.src.training.datasets.download_datasets import download_and_cache
from api.src.ressource.ressource import router
from bdd.database import Base, engine
import tensorflow as tf
from bdd.database import get_db
from api.src.service.service import create_user
from bdd.models import User
from sqlalchemy.orm import Session


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

def parse_default_users():
    users_raw = os.getenv("DEFAULT_USERS", "")
    users = []
    for entry in users_raw.split(","):
        parts = entry.strip().split(":")
        if len(parts) == 5:
            users.append({
                "nom":      parts[0],
                "prenom":   parts[1],
                "email":    parts[2],
                "password": parts[3],
                "admin":    parts[4]
            })
    return users

def seed_default_users():
    db: Session = get_db()  
    try:
        for user in parse_default_users():
            existing = db.query(User).filter(User.email == user["email"]).first()
            if not existing:  
                create_user(
                    db=db,
                    nom=user["nom"],
                    prenom=user["prenom"],
                    email=user["email"],
                    password=user["password"],
                    admin=user["admin"]
                )
    finally:
        db.close()


app.include_router(router)

print("telechargement de fashion_minst")
print()
download_and_cache("fashion_mnist", tf.keras.datasets.fashion_mnist.load_data, 10,  28*28)
print("telechargement de cifar100")
print()
download_and_cache("cifar100",      tf.keras.datasets.cifar100.load_data,      100, 32*32*3)
print("telechargement terminé")
print()

