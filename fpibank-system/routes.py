from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from database import get_db
from dependencies import get_current_user
from models import User, Account, Operation, Log
from schemas import TransferRequest
from decimal import Decimal
import auth
import httpx

router = APIRouter()

EXCHANGE_API_URL = "https://api.exchangerate-api.com/v4/latest/"

async def get_exchange_rate_func(from_currency: str, to_currency: str) -> float:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{EXCHANGE_API_URL}/{from_currency.upper()}")
        if response.status_code != 200:
            raise HTTPException(status_code=502, detail="Ошибка получения курса валют")
        data = response.json()
        rate = data["rates"].get(to_currency.upper())
        if not rate:
            raise HTTPException(status_code=400, detail=f"Неподдерживаемая валюта {to_currency}")
        return float(rate)

@router.post("/transfer")
async def transfer_funds(
    data: TransferRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    if user.email == data.target_email:
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

@router.get("/operations")
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

@router.get("/logs")
def get_logs(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    logs = db.query(Log).filter(Log.user_id == user.id).order_by(Log.timestamp.desc()).all()
    return [{"action": log.action, "timestamp": log.timestamp} for log in logs]



@router.get("/exchange-rate/{base}/{target}")
async def get_exchange_rate(base: str = "USD", target: str = "EUR"):
    """
    Возвращает текущий курс обмена из базовой валюты (base) в целевую (target).
    Например: /exchange-rate/USD/EUR
    """
    url = f"{EXCHANGE_API_URL}/{base.upper()}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)

    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="Ошибка при получении данных от сервиса курсов валют")

    data = response.json()
    rates = data.get("rates", {})

    target_rate = rates.get(target.upper())

    if not target_rate:
        raise HTTPException(status_code=400, detail=f"Целевая валюта {target} не найдена")

    return {
        "base": base.upper(),
        "target": target.upper(),
        "rate": target_rate,
        "updated": data.get("updated", None)
    }

@router.get("/me")
def get_me(user: User = Depends(get_current_user)):
    return {
        "id": user.id,
        "email": user.email,
        "created_at": user.created_at,
        "balances": {acc.currency: float(acc.balance) for acc in user.accounts}
    }

@router.get("/balance")
def get_balance(user: User = Depends(get_current_user)):
    return {"balances": {acc.currency: float(acc.balance) for acc in user.accounts}}