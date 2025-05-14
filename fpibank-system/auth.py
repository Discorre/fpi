from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from database import get_db
from models import User, Account, Log
from schemas import UserCreate, Token
import os
import schemas

router = APIRouter(prefix="/auth")

SECRET_KEY = os.getenv("SECRET_KEY", "secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = pwd_context.hash(user.password)
    new_user = User(email=user.email, hashed_password=hashed)
    db.add(new_user)
    db.flush()
    db.add(Account(user_id=new_user.id, balance=500))
    db.add(Log(user_id=new_user.id, action="Registered"))
    db.commit()
    return {"message": "User registered"}

@router.post("/login")
def login(user: UserCreate, db: Session = Depends(get_db)) -> Token:
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not pwd_context.verify(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access = create_token({"user_id": db_user.id}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    refresh = create_token({"user_id": db_user.id}, timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
    db.add(Log(user_id=db_user.id, action="Logged in"))
    db.commit()
    return Token(access_token=access, refresh_token=refresh)

@router.post("/refresh")
def refresh_token(request: schemas.RefreshTokenRequest) -> Token:
    try:
        payload = jwt.decode(request.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    access = create_token({"user_id": user_id}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    refresh = create_token({"user_id": user_id}, timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
    return Token(access_token=access, refresh_token=refresh)