# models.py
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime, func, Float
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())

    accounts = relationship("Account", back_populates="user")
    logs = relationship("Log", back_populates="user")

class Account(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    currency = Column(String, default="USD")  # например: USD, EUR, RUB
    balance = Column(Numeric(precision=15, scale=2), default=0.00)

    user = relationship("User", back_populates="accounts")
    sent_operations = relationship("Operation", foreign_keys="Operation.sender_account_id")
    received_operations = relationship("Operation", foreign_keys="Operation.receiver_account_id")

class Operation(Base):
    __tablename__ = "operations"
    id = Column(Integer, primary_key=True, index=True)
    sender_account_id = Column(Integer, ForeignKey("accounts.id"))
    receiver_account_id = Column(Integer, ForeignKey("accounts.id"))
    amount = Column(Numeric(precision=15, scale=2), nullable=False)
    converted_amount = Column(Numeric(precision=15, scale=2))  # сумма после конвертации
    currency_from = Column(String)  # валюта отправителя
    currency_to = Column(String)    # валюта получателя
    exchange_rate = Column(Numeric(precision=10, scale=6))     # курс обмена
    timestamp = Column(DateTime, default=func.now())

class Log(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String, nullable=False)
    timestamp = Column(DateTime, default=func.now())
    user = relationship("User", back_populates="logs")

class ExchangeRate(Base):
    __tablename__ = "exchange_rates"
    
    base = Column(String(3), primary_key=True)
    target = Column(String(3), primary_key=True)
    rate = Column(Float, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow)
    next_update = Column(DateTime, default=lambda: datetime.utcnow() + datetime.timedelta(minutes=20))