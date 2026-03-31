from pydantic import BaseModel, ConfigDict, Field, EmailStr

class ModelResponseToFront(BaseModel):
    name : str = Field(..., description="Le nom de la route recommandée")
    accuracies : list[float] 
    isFinished : bool

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
    

#recup le nom du dataset sur lequel on veut train nos modèles
class BenchmarkRequest(BaseModel):
    dataset: str
    epochs: int = 15