# tests/test_api.py
import pytest
from fastapi import status
from httpx import AsyncClient

REGISTER_URL = "/auth/register"
LOGIN_URL = "/auth/login"
TRANSFER_URL = "/transfer"
BALANCE_URL = "/balance"
OPERATIONS_URL = "/operations"


@pytest.mark.asyncio
async def test_register_login_logout(client):
    # Регистрация
    reg_data = {"email": "test@example.com", "password": "password"}
    response = await client.post(REGISTER_URL, json=reg_data)
    assert response.status_code == 200

    # Логин
    login_data = {"email": "test@example.com", "password": "password"}
    response = await client.post(LOGIN_URL, json=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data

    return data["access_token"]


@pytest.mark.asyncio
async def test_get_balance(client):
    token = await test_register_login_logout(client)

    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get(BALANCE_URL, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "balances" in data
    assert "USD" in data["balances"]
    assert data["balances"]["USD"] == 0.0


@pytest.mark.asyncio
async def test_transfer_funds(client):
    token = await test_register_login_logout(client)

    # Зарегистрируем второго пользователя
    async with AsyncClient(app=app, base_url="http://test") as ac:
        reg_data = {"email": "user2@example.com", "password": "password"}
        response = await ac.post("/auth/register")
        assert response.status_code == 200

    headers = {"Authorization": f"Bearer {token}"}

    transfer_data = {
        "target_email": "user2@example.com",
        "amount": 50,
        "from_currency": "USD",
        "to_currency": "EUR"
    }

    response = await client.post(TRANSFER_URL, json=transfer_data, headers=headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Перевод выполнен успешно"


@pytest.mark.asyncio
async def test_operations_history(client):
    token = await test_register_login_logout(client)

    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get(OPERATIONS_URL, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "operations" in data
    assert len(data["operations"]) >= 1