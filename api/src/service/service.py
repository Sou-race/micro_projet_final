import csv
from datetime import datetime, timedelta
from datetime import datetime, timedelta
import json
import os
import threading
from dotenv import load_dotenv
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from bdd.database import get_db
from fastapi import Depends
from sqlalchemy.orm import Session
from api.src.model.model import ModelResponseToFront
from bdd.models import User
from api.src.kafkaOption.consumer import _make_consumer

import bcrypt

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="prouteur/api/login")

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



def _consumer_loop_logs(topic):
    print("test")
    consumer = _make_consumer(topic)
    csv_file = "/app/api/src/logs_login.csv"
    
    folder = os.path.dirname(csv_file)
    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
    
    file_exists = os.path.isfile(csv_file)
    print("test du file",file_exists)
    with open(csv_file, mode='a', newline='', encoding='utf-8') as f:


        fieldnames = ['id', 'nom', 'prenom', 'admin', 'type'] 
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
            f.flush()
            os.fsync(f.fileno())

        while True:
            try:
                msg = consumer.poll(1.0)
                if msg is None:
                    continue
                if msg.error():
                    print(f"Kafka error [{topic}]: {msg.error()}")
                    continue
                data = json.loads(msg.value().decode("utf-8"))
                print(data)
                writer.writerow({
                        'id': data.get('id'),
                        'nom': data.get('nom'),
                        'prenom': data.get('prenom'),
                        'admin': data.get('admin'),
                        'type': data.get('type')

                    })
                    
                f.flush()
                os.fsync(f.fileno())
                
            except Exception as e:
                print(f"Consumer error [{topic}]: {e}")

threading.Thread(target=_consumer_loop_logs, args=("loginLog",), daemon=True).start()



def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    # On vérifie que l'utilisateur existe toujours en base
    user = db.query(User).filter(User.email == email).first() 
    if user is None:
        raise credentials_exception
    return user

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

