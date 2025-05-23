from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    email: str
    password: str

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
    email: str
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