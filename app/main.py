from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .db import engine, Base, get_db
from . import models
from .models import User, Todo
from .config import JWT_SECRET, JWT_ALG, ACCESS_TOKEN_EXPIRE_MIN

app = FastAPI()

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

@app.get("/health")
def health():
    return {"status": "ok"}

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

class UserCreate(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TodoCreate(BaseModel):
    title: str

class TodoOut(BaseModel):
    id: int
    title: str
    done: bool
    class Config:
        from_attributes = True

def hash_password(p: str) -> str:
    return pwd_context.hash(p)

def verify_password(p: str, hashed: str) -> bool:
    return pwd_context.verify(p, hashed)

def create_access_token(sub: str, minutes: int) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": sub,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=minutes)).timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)

def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        sub = payload.get("sub")
        if not sub:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.email == sub).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@app.post("/auth/register")
def register(data: UserCreate, db: Annotated[Session, Depends(get_db)]):
    exists = db.query(User).filter(User.email == data.email).first()
    if exists:
        raise HTTPException(status_code=409, detail="Email already registered")
    user = User(email=data.email, hashed_password=hash_password(data.password))
    db.add(user)
    db.commit()
    return {"result": "ok"}

@app.post("/auth/token", response_model=Token)
def token(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)],
):
    user = db.query(User).filter(User.email == form.username).first()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    access = create_access_token(user.email, ACCESS_TOKEN_EXPIRE_MIN)
    return Token(access_token=access)

@app.post("/todos", response_model=TodoOut)
def create_todo(
    data: TodoCreate,
    db: Annotated[Session, Depends(get_db)],
    me: Annotated[User, Depends(get_current_user)],
):
    todo = Todo(title=data.title, done=False, owner_id=me.id)
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo

@app.get("/todos", response_model=list[TodoOut])
def list_todos(
    db: Annotated[Session, Depends(get_db)],
    me: Annotated[User, Depends(get_current_user)],
):
    return db.query(Todo).filter(Todo.owner_id == me.id).order_by(Todo.id.desc()).all()

@app.patch("/todos/{todo_id}", response_model=TodoOut)
def toggle_done(
    todo_id: int,
    db: Annotated[Session, Depends(get_db)],
    me: Annotated[User, Depends(get_current_user)],
):
    todo = db.query(Todo).filter(Todo.id == todo_id, Todo.owner_id == me.id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    todo.done = not todo.done
    db.commit()
    db.refresh(todo)
    return todo

@app.delete("/todos/{todo_id}")
def delete_todo(
    todo_id: int,
    db: Annotated[Session, Depends(get_db)],
    me: Annotated[User, Depends(get_current_user)],
):
    todo = db.query(Todo).filter(Todo.id == todo_id, Todo.owner_id == me.id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(todo)
    db.commit()
    return {"result": "deleted"}
