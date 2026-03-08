from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.src.ressource.ressource import router
from bdd.database import Base, engine

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


