from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime
import re

class UserCreate(BaseModel):
    email: EmailStr
    password: str

    @validator("email")
    def validate_clean_email(cls, v):
        # Запрещаем любые HTML-теги и скрипты
        if re.search(r"[<>]", v):
            raise ValueError("Email содержит недопустимые символы")

        # Дополнительно: можно блокировать потенциально подозрительные шаблоны
        if "script" in v.lower():
            raise ValueError("Email содержит запрещённое содержимое")

        return v

class Token(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None

class TokenPayload(BaseModel):
    user_id: int
    exp: int

class TokenRefresh(BaseModel):
    refresh_token: str

class TransferRequest(BaseModel):
    target_email: str
    amount: float
    from_currency: str = "USD"
    to_currency: str = "USD"

class MeResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime
    balances: dict[str, float]

class OperationOut(BaseModel):
    amount: float
    converted_amount: float
    from_currency: str
    to_currency: str
    exchange_rate: float
    at: datetime

class LogsOut(BaseModel):
    action: str
    timestamp: datetime

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class LogoutWithRefresh(BaseModel):
    refresh_token: str