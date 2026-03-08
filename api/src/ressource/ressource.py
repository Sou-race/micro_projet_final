from prometheus_client import Counter
import httpx
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from api.src.model.model import ModelResponseToFront
from api.src.service.service import test, create_user, verify_user
from bdd.database import get_db

router = APIRouter(prefix="/prouteur", tags=["Prouteur"])

health_counter = Counter(
    "Health_check_requests_total",
    "Number of health check requests received"
)

#classe de connexion  
class LoginRequest(BaseModel):
    email: str
    password: str

#classe d'inscription
class RegisterRequest(BaseModel):
    nom: str
    prenom: str
    email: EmailStr
    password: str

@router.get("/api/health")
async def health():
    health_counter.inc()
    return {"status": "ok"}

@router.post("/api/register")
def register(data: RegisterRequest, db: Session = Depends(get_db)):

    user = create_user(
        db,
        data.nom,
        data.prenom,
        data.email,
        data.password
    )

    if not user:
        raise HTTPException(status_code=400, detail="Email déjà utilisé")

    return {
        "success": True,
        "message": "Utilisateur créé",
        "user": {
            "id": user.id,
            "nom": user.nom,
            "prenom": user.prenom,
            "email": user.email
        }
    }

@router.post("/api/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = verify_user(db, data.email, data.password)

    if not user:
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")

    return {
        "success": True,
        "message": "Connexion réussie",
        "user": {
            "id": user.id,
            "email": user.email
        }
    }

@router.get("/current", response_model=ModelResponseToFront)
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