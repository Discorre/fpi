from fastapi import APIRouter, Depends, HTTPException, Header, Body
from sqlalchemy.orm import Session
from database import get_db
from dependencies import get_current_user
from models import User, Account, Operation, Log, ExchangeRate
from schemas import TransferRequest
from decimal import Decimal
from fastapi_limiter.depends import RateLimiter
import httpx
import httpx
import asyncio
from datetime import datetime, timedelta

router = APIRouter()
EXCHANGE_API_URL = "https://v6.exchangerate-api.com/v6/a4353249caf64d885434ac6c/pair"
SUPPORTED_CURRENCIES = {"USD", "EUR", "RUB"}

async def get_exchange_rate_func(from_currency: str, to_currency: str) -> float:
    url = f"https://v6.exchangerate-api.com/v6/a4353249caf64d885434ac6c/pair/{from_currency.upper()}/{to_currency.upper()}"
    print(f"Запрашиваю курс: {url}")

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url)
        print(response)
        if response.status_code != 200:
            raise HTTPException(status_code=502, detail="Ошибка получения курса валют")
        
        data = response.json()
        
        if data["result"] != "success":
            raise HTTPException(status_code=502, detail="Ошибка при получении данных от API")

        return float(data["conversion_rate"])

async def update_exchange_rate(db: Session, base: str, target: str):
    url = f"https://v6.exchangerate-api.com/v6/a4353249caf64d885434ac6c/pair/{base.upper()}/{target.upper()}"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url)
        if response.status_code != 200:
            raise HTTPException(status_code=502, detail="Ошибка получения данных от API")
        
        data = response.json()
        if data.get("result") != "success":
            raise HTTPException(status_code=502, detail="Ошибка при получении данных от API")

    rate = float(data["conversion_rate"])
    now = datetime.utcnow()
    next_update = now + timedelta(minutes=20)

    # Сохраняем или обновляем курс
    db_rate = db.query(ExchangeRate).filter(
        ExchangeRate.base == base.upper(),
        ExchangeRate.target == target.upper()
    ).first()

    if db_rate:
        db_rate.rate = rate
        db_rate.updated_at = now
        db_rate.next_update = next_update
    else:
        db_rate = ExchangeRate(
            base=base.upper(),
            target=target.upper(),
            rate=rate,
            updated_at=now,
            next_update=next_update
        )
        db.add(db_rate)

    db.commit()
    return db_rate


async def get_cached_exchange_rate(db: Session, base: str, target: str):
    now = datetime.utcnow()
    db_rate = db.query(ExchangeRate).filter(
        ExchangeRate.base == base.upper(),
        ExchangeRate.target == target.upper()
    ).first()

    if not db_rate or db_rate.next_update < now:
        await update_exchange_rate(db, base, target)
        # Обновляем после обновления
        db_rate = db.query(ExchangeRate).filter(
            ExchangeRate.base == base.upper(),
            ExchangeRate.target == target.upper()
        ).first()

    if not db_rate:
        raise HTTPException(status_code=404, detail="Курс не найден")

    return {
        "base": db_rate.base,
        "target": db_rate.target,
        "rate": db_rate.rate,
        "updated": db_rate.updated_at,
        "next_update": db_rate.next_update
    }

@router.post("/api/v1/transfer", dependencies=[Depends(RateLimiter(times=1, seconds=5))])
async def transfer_funds(
    data: TransferRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    if user.email == data.target_email and data.from_currency == data.to_currency:
        raise HTTPException(status_code=400, detail="Нельзя переводить самому себе")

    sender_account = db.query(Account).filter(
        Account.user_id == user.id, Account.currency == data.from_currency.upper()
    ).first()
    if not sender_account:
        raise HTTPException(status_code=404, detail="Счет в указанной валюте не найден")

    target_user = db.query(User).filter(User.email == data.target_email).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    receiver_account = db.query(Account).filter(
        Account.user_id == target_user.id, Account.currency == data.to_currency.upper()
    ).first()
    if not receiver_account:
        raise HTTPException(status_code=404, detail="Счет получателя в указанной валюте не найден")

    amount = Decimal(str(data.amount))
    if sender_account.balance < amount:
        raise HTTPException(status_code=400, detail="Недостаточно средств")

    exchange_rate = await get_exchange_rate_func(data.from_currency, data.to_currency)
    converted_amount = amount * Decimal(str(exchange_rate))

    # Выполняем перевод
    sender_account.balance -= amount
    receiver_account.balance += converted_amount

    operation = Operation(
        sender_account_id=sender_account.id,
        receiver_account_id=receiver_account.id,
        amount=amount,
        converted_amount=converted_amount,
        currency_from=data.from_currency.upper(),
        currency_to=data.to_currency.upper(),
        exchange_rate=exchange_rate
    )
    db.add(operation)
    db.add(Log(user_id=user.id, action=f"Перевел {amount} {data.from_currency} → {converted_amount} {data.to_currency} пользователю {target_user.email}"))
    db.add(Log(user_id=target_user.id, action=f"Получил {converted_amount} {data.to_currency} от {user.email}"))
    db.commit()

    return {"message": "Перевод выполнен успешно"}

@router.get("/api/v1/operations")
def get_operations(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    operations = db.query(Operation).join(Account, Operation.sender_account_id == Account.id).filter(Account.user_id == user.id).all()
    result = []
    for op in operations:
        result.append({
            "amount": float(op.amount),
            "converted_amount": float(op.converted_amount),
            "from_currency": op.currency_from,
            "to_currency": op.currency_to,
            "exchange_rate": float(op.exchange_rate),
            "at": op.timestamp
        })
    return {"operations": result}

@router.get("/api/v1/logs")
def get_logs(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    logs = db.query(Log).filter(Log.user_id == user.id).order_by(Log.timestamp.desc()).all()
    return [{"action": log.action, "timestamp": log.timestamp} for log in logs]

@router.get("/api/v1/exchange-rate/{base}/{target}")
async def get_exchange_rate_route(
    base: str = "USD",
    target: str = "EUR",
    db: Session = Depends(get_db)
):
    rate_info = await get_cached_exchange_rate(db, base, target)

    return {
        "base": rate_info["base"],
        "target": rate_info["target"],
        "rate": rate_info["rate"],
        "updated": rate_info["updated"],
        "next_update": rate_info["next_update"]
    }

@router.get("/api/v1/me")
def get_me(user: User = Depends(get_current_user)):
    return {
        "id": user.id,
        "email": user.email,
        "created_at": user.created_at,
        "balances": {acc.currency: float(acc.balance) for acc in user.accounts}
    }

@router.get("/api/v1/balance")
def get_balance(user: User = Depends(get_current_user)):
    return {"balances": {acc.currency: float(acc.balance) for acc in user.accounts}}

SUPPORTED_CURRENCIES = {"USD", "EUR", "RUB"}

@router.post("/api/v1/manage-account")
async def manage_account(
    action: str = Body(..., description="Только 'add'"),
    currency: str = Body(..., description="Валюта: USD, EUR, RUB"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    currency = currency.upper()

    if action != "add":
        raise HTTPException(status_code=400, detail="Неверное действие. Разрешено только 'add'")

    if currency not in SUPPORTED_CURRENCIES:
        raise HTTPException(status_code=400, detail="Недопустимая валюта")

    existing = db.query(Account).filter(Account.user_id == user.id, Account.currency == currency).first()
    if existing:
        raise HTTPException(status_code=400, detail="Счет в этой валюте уже существует")

    new_account = Account(user_id=user.id, currency=currency, balance=Decimal("0.00"))
    db.add(new_account)
    db.add(Log(user_id=user.id, action=f"Создан счёт в валюте {currency}"))
    db.commit()
    db.refresh(new_account)

    return {
        "message": f"Счёт в валюте {currency} успешно создан",
        "account": {
            "currency": new_account.currency,
            "balance": float(new_account.balance)
        }
    }