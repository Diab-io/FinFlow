import os
import hmac
import json
import hashlib
import pytest
import fakeredis

import app.core.redis as redis_module
redis_module.redis_client = fakeredis.FakeRedis(decode_responses=True)
from unittest.mock import patch
from dotenv import load_dotenv

load_dotenv()

from app.main import app
from app.core.database import Base, get_db
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

TEST_DATABASE_URI = os.getenv('TEST_DATABASE_URL')
WEBHOOK_KEY = os.getenv('WEBHOOK_KEY')

engine = create_engine(TEST_DATABASE_URI)
TestSession = sessionmaker(bind=engine)


@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    session = TestSession()
    yield session
    session.close()
    Base.metadata.drop_all(engine)


@pytest.fixture
def client(db):
    def get_override_db():
        yield db

    app.dependency_overrides[get_db] = get_override_db
    yield TestClient(app)
    app.dependency_overrides.clear()


# ── User fixtures ──

@pytest.fixture
def register_user(client):
    payload = {
        "username": "john.doe",
        "email": "test@example.com",
        "password": "example"
    }
    client.post('/api/auth/register', json=payload)
    return payload


@pytest.fixture
def token(client, register_user):
    resp = client.post('/api/auth/token', json=register_user)
    return resp.json()["access_token"]


@pytest.fixture
def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def second_user(client):
    payload = {
        "username": "jane.doe",
        "email": "jane@example.com",
        "password": "example"
    }
    client.post('/api/auth/register', json=payload)
    return payload


@pytest.fixture
def second_token(client, second_user):
    resp = client.post('/api/auth/token', json=second_user)
    return resp.json()["access_token"]


@pytest.fixture
def second_auth_headers(second_token):
    return {"Authorization": f"Bearer {second_token}"}


# ── Wallet & funding helpers ──

def sign_webhook_payload(payload_dict: dict) -> tuple[str, str]:
    """Create a signed webhook payload like the mock gateway would."""
    payload_str = json.dumps(payload_dict)
    signature = hmac.new(
        WEBHOOK_KEY.encode("utf-8"),
        payload_str.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()
    return payload_str, signature


def fund_user_wallet(client, auth_headers, amount: float = 10000) -> str:
    """Fund a user's wallet by simulating the full payment flow.
    Returns the payment reference.
    """
    with patch("app.payments.service.requests.post"):
        resp = client.post(
            "/api/payments/fund",
            json={"amount": amount},
            headers=auth_headers
        )
    payment_data = resp.json()
    reference = payment_data["reference"]

    webhook_payload = {"reference": reference, "status": "success"}
    payload_str, signature = sign_webhook_payload(webhook_payload)

    client.post(
        "/api/payments/webhook",
        content=payload_str,
        headers={
            "Content-Type": "application/json",
            "x-webhook-signature": signature
        }
    )
    return reference


@pytest.fixture
def funded_user(client, auth_headers):
    """First user with 10,000 in their wallet."""
    fund_user_wallet(client, auth_headers, amount=10000)
    return auth_headers


@pytest.fixture
def recipient_account(client, second_auth_headers):
    """Returns the account number of the second user's wallet."""
    resp = client.get("/api/wallets/me", headers=second_auth_headers)
    return resp.json()["account_number"]