import uuid
from .conftest import client, register_user, token

def test_register_user(client):
    payload = {
        "username": "diab",
        "email": "test@example.com",
        "password": "example"
    }

    response = client.post('/api/auth/register', json=payload)
    data = response.json()
    assert response.status_code == 201
    assert payload["email"] == data["email"]
    assert "id" in data

def test_missing_username(client):
    resp = client.post('/api/auth/register', json={
        "email": f"test_{uuid.uuid4()}@example.com",
        "password": "example"
    })

    assert resp.status_code == 422

def test_missing_email(client):
    resp = client.post('/api/auth/register', json={
        "username": "diablo",
        "password": "example"
    })

    assert resp.status_code == 422

def test_missing_password(client):
    resp = client.post('/api/auth/register', json={
        "username": "diablo",
        "email": f"test_{uuid.uuid4()}@example.com"
    })

    assert resp.status_code == 422

def test_duplicate_email(client, register_user):
    resp = client.post('/api/auth/register', json={
        "username": "diablo",
        "email": register_user["email"],
        "password": "example"
    })
    assert resp.status_code == 409
    assert resp.json()['detail'] == "User already exists"


def test_duplicate_username(client, register_user):    
    resp = client.post('/api/auth/register', json={
        "username": register_user["username"],
        "email": f"test_{uuid.uuid4()}@example.com",
        "password": "example"
    })
    assert resp.status_code == 409
    assert resp.json()['detail'] == "Username already taken"

def test_user_login(client, register_user):
    resp = client.post('/api/auth/token', json={
        "email": register_user["email"],
        "password": register_user["password"]
    })
    data = resp.json()
    assert resp.status_code == 200
    assert "access_token" in data
    assert len(data["access_token"].split('.')) == 3

def test_wrong_password(client, register_user):
    resp = client.post('/api/auth/token', json={
        "email": register_user["email"],
        "password": "abc1234"
    })
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Incorrect username or password"

def test_user_not_found(client, register_user):
    resp = client.post('/api/auth/token', json={
        "email": f"test_{uuid.uuid4()}@example.com",
        "password": register_user["password"]
    })
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Incorrect username or password"

