from pydantic import BaseModel, ConfigDict, Field

class ModelResponseToFront(BaseModel):
    name : str = Field(..., description="Le nom de la route recommandée")
    accuracies : list[float] 
    isFinished : bool