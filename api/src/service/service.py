from api.src.model.model import ModelResponseToFront
from bdd.models import User
import bcrypt

#juste un test pour voir que tout marche dans ressource
def test():
    res =ModelResponseToFront(
        name="test",
        accuracies=[0.1, 0.2, 0.3],
        isFinished=True
    )
    return res

def test():
    return {
        "title": "test",
        "description": "réponse de test"
    }

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))

def create_user(db, nom, prenom, email, password, admin):
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        return None

    hashed_password = hash_password(password)

    user = User(
        nom=nom,
        prenom=prenom,
        email=email,
        password=hashed_password,
        admin= admin
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def verify_user(db, email, password):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None

    if not verify_password(password, user.password):
        return None

    return user