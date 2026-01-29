from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import os

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from models import Base, User

load_dotenv()

DB_USER = os.getenv("DB_USER", "app")
DB_PASSWORD = os.getenv("DB_PASSWORD", "apppass")
DB_NAME = os.getenv("DB_NAME", "appdb")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

DATABASE_URL = f"postgresql+psycopg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

app = FastAPI()

class UserCreate(BaseModel):
    name: str

class UserUpdate(BaseModel):
    name: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/db")
def db_check():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1")).scalar_one()
    return {"db": "ok", "result": result}

@app.post("/users")
def create_user(payload: UserCreate):
    with Session(engine) as session:
        user = User(name=payload.name)
        session.add(user)
        session.commit()
        session.refresh(user)
        return {"id": user.id, "name": user.name}

@app.get("/users")
def list_users():
    with Session(engine) as session:
        users = session.query(User).order_by(User.id).all()
        return [{"id": u.id, "name": u.name} for u in users]

@app.get("/users/{user_id}")
def get_user(user_id: int):
    with Session(engine) as session:
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return {"id": user.id, "name": user.name}

@app.put("/users/{user_id}")
def update_user(user_id: int, payload: UserUpdate):
    with Session(engine) as session:
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user.name = payload.name
        session.commit()
        session.refresh(user)
        return {"id": user.id, "name": user.name}

@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    with Session(engine) as session:
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        session.delete(user)
        session.commit()
        return {"deleted": True, "id": user_id}
