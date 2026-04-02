import uuid
from .conftest import (
    client, auth_headers, token, register_user,
    second_auth_headers, second_user, second_token,
    funded_user, recipient_account,
    fund_user_wallet
)


# ── Wallet details ──

def test_wallet_created_on_registration(client, auth_headers):
    resp = client.get("/api/wallets/me", headers=auth_headers)
    data = resp.json()
    assert resp.status_code == 200
    assert "user_id" in data
    assert "account_number" in data
    assert len(data["account_number"]) == 10


def test_wallet_default_currency_is_ngn(client, auth_headers):
    resp = client.get("/api/wallets/me", headers=auth_headers)
    assert resp.json()["currency"] == "NGN"


def test_wallet_with_specified_currency(client):
    email = f"test_{uuid.uuid4()}@example.com"
    client.post("/api/auth/register", json={
        "username": f"user_{uuid.uuid4().hex[:6]}",
        "email": email,
        "password": "example",
        "currency": "USD"
    })
    login = client.post("/api/auth/token", json={
        "email": email,
        "password": "example"
    })
    token = login.json()["access_token"]

    resp = client.get("/api/wallets/me", headers={
        "Authorization": f"Bearer {token}"
    })
    assert resp.status_code == 200
    assert resp.json()["currency"] == "USD"


def test_wallet_no_auth(client):
    resp = client.get("/api/wallets/me")
    assert resp.status_code == 401


def test_each_user_gets_unique_account_number(client, auth_headers, second_auth_headers):
    wallet1 = client.get("/api/wallets/me", headers=auth_headers)
    wallet2 = client.get("/api/wallets/me", headers=second_auth_headers)

    assert wallet1.json()["account_number"] != wallet2.json()["account_number"]


# ── Balance ──

def test_new_wallet_balance_is_zero(client, auth_headers):
    resp = client.get("/api/wallets/me/balance", headers=auth_headers)
    data = resp.json()
    assert resp.status_code == 200
    assert float(data["balance"]) == 0
    assert "currency" in data


def test_balance_after_funding(client, auth_headers):
    fund_user_wallet(client, auth_headers, amount=5000)

    resp = client.get("/api/wallets/me/balance", headers=auth_headers)
    assert float(resp.json()["balance"]) == 5000


def test_balance_after_multiple_fundings(client, auth_headers):
    fund_user_wallet(client, auth_headers, amount=3000)
    fund_user_wallet(client, auth_headers, amount=7000)

    resp = client.get("/api/wallets/me/balance", headers=auth_headers)
    assert float(resp.json()["balance"]) == 10000


def test_balance_after_transfer_sender(client, funded_user, recipient_account):
    client.post("/api/transfers/", json={
        "account_number": recipient_account,
        "amount": 4000
    }, headers={**funded_user, "x-idempotency-key": str(uuid.uuid4())})

    resp = client.get("/api/wallets/me/balance", headers=funded_user)
    assert float(resp.json()["balance"]) == 6000


def test_balance_after_transfer_receiver(client, funded_user, recipient_account, second_auth_headers):
    client.post("/api/transfers/", json={
        "account_number": recipient_account,
        "amount": 2500
    }, headers={**funded_user, "x-idempotency-key": str(uuid.uuid4())})

    resp = client.get("/api/wallets/me/balance", headers=second_auth_headers)
    assert float(resp.json()["balance"]) == 2500


def test_balance_no_auth(client):
    resp = client.get("/api/wallets/me/balance")
    assert resp.status_code == 401


# ── Transaction history ──

def test_empty_transaction_history(client, auth_headers):
    resp = client.get("/api/wallets/me/transactions", headers=auth_headers)
    data = resp.json()
    assert resp.status_code == 200
    assert data["data"] == []
    assert data["meta"]["total_items"] == 0


def test_transaction_history_after_funding(client, auth_headers):
    fund_user_wallet(client, auth_headers, amount=5000)

    resp = client.get("/api/wallets/me/transactions", headers=auth_headers)
    data = resp.json()
    assert len(data["data"]) == 1
    assert data["data"][0]["type"] == "CREDIT"
    assert float(data["data"][0]["amount"]) == 5000


def test_transaction_history_after_transfer(client, funded_user, recipient_account):
    client.post("/api/transfers/", json={
        "account_number": recipient_account,
        "amount": 3000
    }, headers={**funded_user, "x-idempotency-key": str(uuid.uuid4())})

    resp = client.get("/api/wallets/me/transactions", headers=funded_user)
    transactions = resp.json()["data"]

    # Sender should see: 1 credit (funding) + 1 debit (transfer)
    types = [t["type"] for t in transactions]
    assert "CREDIT" in types
    assert "DEBIT" in types


def test_transaction_history_shows_receiver_credit(client, funded_user, recipient_account, second_auth_headers):
    client.post("/api/transfers/", json={
        "account_number": recipient_account,
        "amount": 1500
    }, headers={**funded_user, "x-idempotency-key": str(uuid.uuid4())})

    resp = client.get("/api/wallets/me/transactions", headers=second_auth_headers)
    transactions = resp.json()["data"]

    assert len(transactions) == 1
    assert transactions[0]["type"] == "CREDIT"
    assert float(transactions[0]["amount"]) == 1500


def test_transactions_no_auth(client):
    resp = client.get("/api/wallets/me/transactions")
    assert resp.status_code == 401


# ── Pagination ──

def test_transactions_pagination_meta(client, auth_headers):
    # Fund 3 times to create 3 transactions
    fund_user_wallet(client, auth_headers, amount=1000)
    fund_user_wallet(client, auth_headers, amount=2000)
    fund_user_wallet(client, auth_headers, amount=3000)

    resp = client.get("/api/wallets/me/transactions?page=1&limit=2", headers=auth_headers)
    data = resp.json()

    assert resp.status_code == 200
    assert len(data["data"]) == 2
    assert data["meta"]["page"] == 1
    assert data["meta"]["limit"] == 2
    assert data["meta"]["total_items"] == 3
    assert data["meta"]["total_pages"] == 2


def test_transactions_pagination_second_page(client, auth_headers):
    fund_user_wallet(client, auth_headers, amount=1000)
    fund_user_wallet(client, auth_headers, amount=2000)
    fund_user_wallet(client, auth_headers, amount=3000)

    resp = client.get("/api/wallets/me/transactions?page=2&limit=2", headers=auth_headers)
    data = resp.json()

    assert len(data["data"]) == 1  # Only 1 item on page 2


def test_transactions_pagination_links(client, auth_headers):
    fund_user_wallet(client, auth_headers, amount=1000)
    fund_user_wallet(client, auth_headers, amount=2000)
    fund_user_wallet(client, auth_headers, amount=3000)

    resp = client.get("/api/wallets/me/transactions?page=1&limit=2", headers=auth_headers)
    links = resp.json()["links"]

    assert links["self"] is not None
    assert links["first"] is not None
    assert links["next"] is not None
    assert links["prev"] is None  # No previous on page 1


def test_transactions_default_pagination(client, auth_headers):
    fund_user_wallet(client, auth_headers, amount=1000)

    resp = client.get("/api/wallets/me/transactions", headers=auth_headers)
    meta = resp.json()["meta"]

    assert meta["page"] == 1
    assert meta["limit"] == 10  # Default limit