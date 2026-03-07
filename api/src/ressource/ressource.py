
from collections import Counter

import httpx
from fastapi import APIRouter, FastAPI, HTTPException, Query
from api.src.model.model import ModelResponseToFront
from api.src.service.service import test
from fastapi.middleware.cors import CORSMiddleware

router = APIRouter(prefix="/prouteur", tags=["Prouteur"])

app = FastAPI()
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
health_counter = Counter("Health_check_requests_total", "Number of health check requests received")
    

@app.get("/api/health")
async def health():
    health_counter.inc()
    return {"status": "ok"}

@app.get("/current", response_model=ModelResponseToFront)
async def get_response_to_front():
    
    try:
        #juste un test dans service a remplacer par la vraie fonction qui va faire le travail de recommandation
        response = await test()
        return response

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail=f"Jeu avec ID '{id}' non trouvé.",
            ) from e
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Erreur lors de la récupération des données de jeu: {str(e)}",
        ) from e
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=500, detail=f"Erreur de connexion à l'API de jeux: {str(e)}"
        ) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne du serveur: {str(e)}") from e