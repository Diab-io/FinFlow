import uuid
from .conftest import token, client

def test_wallet_created(client, token):
    resp = client.get('/api/wallets/me', headers={
        "Authorization": f"Bearer {token}"
    })
    data = resp.json()
    assert resp.status_code == 200
    assert "user_id" in data
    assert "account_number" in data

def test_default_wallet_currency(client, token):
    resp = client.get('/api/wallets/me', headers={
        "Authorization": f"Bearer {token}"
    })
    data = resp.json()
    assert resp.status_code == 200
    assert data["currency"] == "NGN"

def test_wallet_specific_currency(client):
    email = f"test_{uuid.uuid4()}@example.com"
    password = "example"

    register = client.post('/api/auth/register', json={
        "username": "test_user",
        "email": email,
        "password": password,
        "currency": "USD"
    })
    assert register.status_code == 201

    login = client.post('/api/auth/token', json={
        "email": email,
        "password": password
    })
    login_data = login.json()
    assert login.status_code == 200
    assert "access_token" in login_data

    token = login_data["access_token"]
    wallet = client.get('/api/wallets/me', headers={
        "Authorization": f"Bearer {token}"
    })
    assert wallet.status_code == 200
    assert wallet.json()["currency"] == "USD"