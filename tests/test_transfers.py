import uuid
from .conftest import (
    client, auth_headers, funded_user, recipient_account,
    second_auth_headers, fund_user_wallet
)


# ── Happy path ──

def test_successful_transfer(client, funded_user, recipient_account):
    idempotency_key = str(uuid.uuid4())

    resp = client.post("/api/transfers/", json={
        "account_number": recipient_account,
        "amount": 3000,
        "description": "Lunch money"
    }, headers={
        **funded_user,
        "x-idempotency-key": idempotency_key
    })
    data = resp.json()

    assert resp.status_code == 200
    assert data["status"] == "completed"
    assert data["account_number"] == recipient_account
    assert float(data["amount"]) == 3000


def test_sender_balance_decreases_after_transfer(client, funded_user, recipient_account):
    client.post("/api/transfers/", json={
        "account_number": recipient_account,
        "amount": 4000
    }, headers={**funded_user, "x-idempotency-key": str(uuid.uuid4())})

    resp = client.get("/api/wallets/me/balance", headers=funded_user)
    balance = float(resp.json()["balance"])
    assert balance == 6000  # 10000 - 4000


def test_receiver_balance_increases_after_transfer(client, funded_user, recipient_account, second_auth_headers):
    client.post("/api/transfers/", json={
        "account_number": recipient_account,
        "amount": 2500
    }, headers={**funded_user, "x-idempotency-key": str(uuid.uuid4())})

    resp = client.get("/api/wallets/me/balance", headers=second_auth_headers)
    balance = float(resp.json()["balance"])
    assert balance == 2500


def test_transfer_creates_two_transactions(client, funded_user, recipient_account):
    resp = client.post("/api/transfers/", json={
        "account_number": recipient_account,
        "amount": 1000
    }, headers={**funded_user, "x-idempotency-key": str(uuid.uuid4())})
    reference = resp.json()["reference"]

    txn_resp = client.get(f"/api/transfers/{reference}", headers=funded_user)
    transactions = txn_resp.json()["transactions"]

    assert len(transactions) == 2

    types = {t["type"] for t in transactions}
    assert "DEBIT" in types
    assert "CREDIT" in types


def test_get_transfer_by_reference(client, funded_user, recipient_account):
    resp = client.post("/api/transfers/", json={
        "account_number": recipient_account,
        "amount": 500
    }, headers={**funded_user, "x-idempotency-key": str(uuid.uuid4())})
    reference = resp.json()["reference"]

    get_resp = client.get(f"/api/transfers/{reference}", headers=funded_user)
    assert get_resp.status_code == 200
    assert "transactions" in get_resp.json()


# ── Validation errors ──

def test_insufficient_funds(client, funded_user, recipient_account):
    resp = client.post("/api/transfers/", json={
        "account_number": recipient_account,
        "amount": 99999
    }, headers={**funded_user, "x-idempotency-key": str(uuid.uuid4())})

    assert resp.status_code == 400
    assert resp.json()["detail"] == "Insufficient funds"


def test_transfer_to_self(client, funded_user, auth_headers):
    # Get own account number
    wallet_resp = client.get("/api/wallets/me", headers=auth_headers)
    own_account = wallet_resp.json()["account_number"]

    resp = client.post("/api/transfers/", json={
        "account_number": own_account,
        "amount": 1000
    }, headers={**funded_user, "x-idempotency-key": str(uuid.uuid4())})

    assert resp.status_code == 400
    assert resp.json()["detail"] == "You can't send funds to yourself"


def test_transfer_to_nonexistent_account(client, funded_user):
    resp = client.post("/api/transfers/", json={
        "account_number": "0000000000",
        "amount": 1000
    }, headers={**funded_user, "x-idempotency-key": str(uuid.uuid4())})

    assert resp.status_code == 404
    assert "wallet" in resp.json()["detail"].lower() or "account" in resp.json()["detail"].lower()


def test_transfer_cross_currency_blocked(client, auth_headers):
    # Create a USD user
    usd_email = f"usd_{uuid.uuid4()}@example.com"
    client.post("/api/auth/register", json={
        "username": "usd_user",
        "email": usd_email,
        "password": "example",
        "currency": "USD"
    })
    usd_login = client.post("/api/auth/token", json={
        "email": usd_email,
        "password": "example"
    })
    usd_token = usd_login.json()["access_token"]
    usd_headers = {"Authorization": f"Bearer {usd_token}"}

    usd_wallet = client.get("/api/wallets/me", headers=usd_headers)
    usd_account = usd_wallet.json()["account_number"]

    # Fund NGN user
    fund_user_wallet(client, auth_headers, amount=5000)

    resp = client.post("/api/transfers/", json={
        "account_number": usd_account,
        "amount": 1000
    }, headers={**auth_headers, "x-idempotency-key": str(uuid.uuid4())})

    assert resp.status_code == 400
    assert "currency" in resp.json()["detail"].lower()


def test_transfer_zero_amount(client, funded_user, recipient_account):
    resp = client.post("/api/transfers/", json={
        "account_number": recipient_account,
        "amount": 0
    }, headers={**funded_user, "x-idempotency-key": str(uuid.uuid4())})

    assert resp.status_code == 422  # Pydantic validation: amount must be >= 1


def test_transfer_negative_amount(client, funded_user, recipient_account):
    resp = client.post("/api/transfers/", json={
        "account_number": recipient_account,
        "amount": -500
    }, headers={**funded_user, "x-idempotency-key": str(uuid.uuid4())})

    assert resp.status_code == 422


def test_transfer_missing_idempotency_key(client, funded_user, recipient_account):
    resp = client.post("/api/transfers/", json={
        "account_number": recipient_account,
        "amount": 1000
    }, headers=funded_user)

    assert resp.status_code == 422  # Missing required header


def test_transfer_no_auth(client, recipient_account):
    resp = client.post("/api/transfers/", json={
        "account_number": recipient_account,
        "amount": 1000
    }, headers={"x-idempotency-key": str(uuid.uuid4())})

    assert resp.status_code == 401


def test_get_nonexistent_reference(client, auth_headers):
    resp = client.get("/api/transfers/FAKE-ref-123", headers=auth_headers)
    assert resp.status_code == 404


# ── Idempotency ──

def test_idempotent_transfer_returns_same_result(client, funded_user, recipient_account):
    idempotency_key = str(uuid.uuid4())
    transfer_payload = {
        "account_number": recipient_account,
        "amount": 2000
    }

    # First request
    resp1 = client.post("/api/transfers/", json=transfer_payload, headers={
        **funded_user, "x-idempotency-key": idempotency_key
    })

    # Second request with same key
    resp2 = client.post("/api/transfers/", json=transfer_payload, headers={
        **funded_user, "x-idempotency-key": idempotency_key
    })

    assert resp1.status_code == 200
    assert resp2.status_code == 200
    assert resp1.json()["reference"] == resp2.json()["reference"]


def test_idempotent_transfer_no_double_debit(client, funded_user, recipient_account):
    idempotency_key = str(uuid.uuid4())
    transfer_payload = {
        "account_number": recipient_account,
        "amount": 5000
    }

    # Send same transfer twice
    client.post("/api/transfers/", json=transfer_payload, headers={
        **funded_user, "x-idempotency-key": idempotency_key
    })
    client.post("/api/transfers/", json=transfer_payload, headers={
        **funded_user, "x-idempotency-key": idempotency_key
    })

    # Balance should reflect only ONE transfer, not two
    resp = client.get("/api/wallets/me/balance", headers=funded_user)
    balance = float(resp.json()["balance"])
    assert balance == 5000  # 10000 - 5000, not 10000 - 10000


def test_different_idempotency_keys_create_separate_transfers(client, funded_user, recipient_account):
    resp1 = client.post("/api/transfers/", json={
        "account_number": recipient_account,
        "amount": 1000
    }, headers={**funded_user, "x-idempotency-key": str(uuid.uuid4())})

    resp2 = client.post("/api/transfers/", json={
        "account_number": recipient_account,
        "amount": 1000
    }, headers={**funded_user, "x-idempotency-key": str(uuid.uuid4())})

    assert resp1.json()["reference"] != resp2.json()["reference"]

    # Balance should reflect both transfers
    balance_resp = client.get("/api/wallets/me/balance", headers=funded_user)
    balance = float(balance_resp.json()["balance"])
    assert balance == 8000  # 10000 - 1000 - 1000