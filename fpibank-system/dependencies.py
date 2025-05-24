# dependencies.py
from fastapi import Depends, HTTPException, status
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from database import get_db
from models import User, ExchangeRate
from auth import SECRET_KEY, ALGORITHM
from fastapi.security import OAuth2PasswordBearer
import auth
from datetime import datetime
import httpx
import asyncio

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        if not auth.is_token_blacklisted(token):
            print(auth.is_token_blacklisted(token))
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Да ты хацкер")
        
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print("Расшифрованная полезная нагрузка:")
        print(payload)
        user_id: int = payload.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Недействительный токен",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не удалось проверить учетные данные",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user

