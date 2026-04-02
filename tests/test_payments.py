import uuid
from unittest.mock import patch
from .conftest import (
    client, auth_headers, token, register_user,
    sign_webhook_payload, fund_user_wallet
)


# ── Initiate funding ──

def test_initiate_funding_creates_pending_payment(client, auth_headers):
    with patch("app.payments.service.requests.post"):
        resp = client.post("/api/payments/fund", json={
            "amount": 5000
        }, headers=auth_headers)

    data = resp.json()
    assert resp.status_code == 200
    assert data["status"] == "PENDING"
    assert "reference" in data
    assert data["reference"].startswith("PAY-")
    assert float(data["amount"]) == 5000


def test_initiate_funding_no_auth(client):
    resp = client.post("/api/payments/fund", json={"amount": 5000})
    assert resp.status_code == 401


def test_initiate_funding_invalid_amount(client, auth_headers):
    resp = client.post("/api/payments/fund", json={
        "amount": 0
    }, headers=auth_headers)
    assert resp.status_code == 422


def test_initiate_funding_negative_amount(client, auth_headers):
    resp = client.post("/api/payments/fund", json={
        "amount": -1000
    }, headers=auth_headers)
    assert resp.status_code == 422


# ── Webhook — success ──

def test_webhook_success_credits_wallet(client, auth_headers):
    # Create pending payment
    with patch("app.payments.service.requests.post"):
        fund_resp = client.post("/api/payments/fund", json={
            "amount": 7500
        }, headers=auth_headers)
    reference = fund_resp.json()["reference"]

    # Simulate gateway success callback
    webhook_payload = {"reference": reference, "status": "success"}
    payload_str, signature = sign_webhook_payload(webhook_payload)

    resp = client.post("/api/payments/webhook",
        content=payload_str,
        headers={
            "Content-Type": "application/json",
            "x-webhook-signature": signature
        }
    )
    assert resp.status_code == 200

    # Verify wallet was credited
    balance_resp = client.get("/api/wallets/me/balance", headers=auth_headers)
    balance = float(balance_resp.json()["balance"])
    assert balance == 7500


def test_webhook_success_updates_payment_status(client, auth_headers):
    with patch("app.payments.service.requests.post"):
        fund_resp = client.post("/api/payments/fund", json={
            "amount": 3000
        }, headers=auth_headers)
    reference = fund_resp.json()["reference"]

    webhook_payload = {"reference": reference, "status": "success"}
    payload_str, signature = sign_webhook_payload(webhook_payload)

    client.post("/api/payments/webhook",
        content=payload_str,
        headers={
            "Content-Type": "application/json",
            "x-webhook-signature": signature
        }
    )

    # Check payment status changed to SUCCESS
    payment_resp = client.get(f"/api/payments/{reference}", headers=auth_headers)
    assert payment_resp.json()["status"] == "SUCCESS"


# ── Webhook — failure ──

def test_webhook_failed_does_not_credit_wallet(client, auth_headers):
    with patch("app.payments.service.requests.post"):
        fund_resp = client.post("/api/payments/fund", json={
            "amount": 5000
        }, headers=auth_headers)
    reference = fund_resp.json()["reference"]

    # Gateway reports failure
    webhook_payload = {"reference": reference, "status": "failed", "reason": "Card declined"}
    payload_str, signature = sign_webhook_payload(webhook_payload)

    resp = client.post("/api/payments/webhook",
        content=payload_str,
        headers={
            "Content-Type": "application/json",
            "x-webhook-signature": signature
        }
    )
    assert resp.status_code == 200

    # Balance should still be 0
    balance_resp = client.get("/api/wallets/me/balance", headers=auth_headers)
    balance = float(balance_resp.json()["balance"])
    assert balance == 0


def test_webhook_failed_updates_payment_status(client, auth_headers):
    with patch("app.payments.service.requests.post"):
        fund_resp = client.post("/api/payments/fund", json={
            "amount": 2000
        }, headers=auth_headers)
    reference = fund_resp.json()["reference"]

    webhook_payload = {"reference": reference, "status": "failed", "reason": "Card declined"}
    payload_str, signature = sign_webhook_payload(webhook_payload)

    client.post("/api/payments/webhook",
        content=payload_str,
        headers={
            "Content-Type": "application/json",
            "x-webhook-signature": signature
        }
    )

    payment_resp = client.get(f"/api/payments/{reference}", headers=auth_headers)
    assert payment_resp.json()["status"] == "FAILED"


# ── Webhook — security ──

def test_webhook_invalid_signature_rejected(client, auth_headers):
    with patch("app.payments.service.requests.post"):
        fund_resp = client.post("/api/payments/fund", json={
            "amount": 5000
        }, headers=auth_headers)
    reference = fund_resp.json()["reference"]

    webhook_payload = {"reference": reference, "status": "success"}
    payload_str = '{"reference": "' + reference + '", "status": "success"}'
    fake_signature = "definitely_not_a_valid_signature"

    resp = client.post("/api/payments/webhook",
        content=payload_str,
        headers={
            "Content-Type": "application/json",
            "x-webhook-signature": fake_signature
        }
    )
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Invalid signature"


def test_webhook_missing_signature_rejected(client):
    resp = client.post("/api/payments/webhook",
        content='{"reference": "PAY-fake123", "status": "success"}',
        headers={"Content-Type": "application/json"}
    )
    assert resp.status_code == 422  # Missing required header


# ── Webhook — edge cases ──

def test_webhook_already_processed(client, auth_headers):
    with patch("app.payments.service.requests.post"):
        fund_resp = client.post("/api/payments/fund", json={
            "amount": 5000
        }, headers=auth_headers)
    reference = fund_resp.json()["reference"]

    webhook_payload = {"reference": reference, "status": "success"}
    payload_str, signature = sign_webhook_payload(webhook_payload)

    webhook_headers = {
        "Content-Type": "application/json",
        "x-webhook-signature": signature
    }

    # First call
    client.post("/api/payments/webhook", content=payload_str, headers=webhook_headers)

    # Second call — same payment, already processed
    resp = client.post("/api/payments/webhook", content=payload_str, headers=webhook_headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "Already Processed"


def test_webhook_already_processed_no_double_credit(client, auth_headers):
    with patch("app.payments.service.requests.post"):
        fund_resp = client.post("/api/payments/fund", json={
            "amount": 5000
        }, headers=auth_headers)
    reference = fund_resp.json()["reference"]

    webhook_payload = {"reference": reference, "status": "success"}
    payload_str, signature = sign_webhook_payload(webhook_payload)

    webhook_headers = {
        "Content-Type": "application/json",
        "x-webhook-signature": signature
    }

    # Call webhook twice
    client.post("/api/payments/webhook", content=payload_str, headers=webhook_headers)
    client.post("/api/payments/webhook", content=payload_str, headers=webhook_headers)

    # Balance should be 5000, not 10000
    balance_resp = client.get("/api/wallets/me/balance", headers=auth_headers)
    balance = float(balance_resp.json()["balance"])
    assert balance == 5000


def test_webhook_nonexistent_reference(client):
    webhook_payload = {"reference": "PAY-doesnotexist", "status": "success"}
    payload_str, signature = sign_webhook_payload(webhook_payload)

    resp = client.post("/api/payments/webhook",
        content=payload_str,
        headers={
            "Content-Type": "application/json",
            "x-webhook-signature": signature
        }
    )
    assert resp.status_code == 404


# ── Get payment status ──

def test_get_payment_by_reference(client, auth_headers):
    with patch("app.payments.service.requests.post"):
        fund_resp = client.post("/api/payments/fund", json={
            "amount": 3000
        }, headers=auth_headers)
    reference = fund_resp.json()["reference"]

    resp = client.get(f"/api/payments/{reference}", headers=auth_headers)
    data = resp.json()

    assert resp.status_code == 200
    assert data["reference"] == reference
    assert data["status"] == "PENDING"
    assert float(data["amount"]) == 3000


def test_get_nonexistent_payment(client, auth_headers):
    resp = client.get("/api/payments/PAY-fake999", headers=auth_headers)
    assert resp.status_code == 404


def test_get_payment_no_auth(client):
    resp = client.get("/api/payments/PAY-fake999")
    assert resp.status_code == 401


# ── Full funding flow ──

def test_full_funding_flow(client, auth_headers):
    """End-to-end: initiate → webhook success → balance updated → payment status SUCCESS."""
    # 1. Check initial balance is 0
    balance_resp = client.get("/api/wallets/me/balance", headers=auth_headers)
    assert float(balance_resp.json()["balance"]) == 0

    # 2. Initiate funding
    with patch("app.payments.service.requests.post"):
        fund_resp = client.post("/api/payments/fund", json={
            "amount": 15000
        }, headers=auth_headers)
    assert fund_resp.status_code == 200
    reference = fund_resp.json()["reference"]

    # 3. Payment should be pending
    payment_resp = client.get(f"/api/payments/{reference}", headers=auth_headers)
    assert payment_resp.json()["status"] == "PENDING"

    # 4. Webhook confirms success
    webhook_payload = {"reference": reference, "status": "success"}
    payload_str, signature = sign_webhook_payload(webhook_payload)
    webhook_resp = client.post("/api/payments/webhook",
        content=payload_str,
        headers={
            "Content-Type": "application/json",
            "x-webhook-signature": signature
        }
    )
    assert webhook_resp.status_code == 200

    # 5. Balance should now be 15000
    balance_resp = client.get("/api/wallets/me/balance", headers=auth_headers)
    assert float(balance_resp.json()["balance"]) == 15000

    # 6. Payment status should be SUCCESS
    payment_resp = client.get(f"/api/payments/{reference}", headers=auth_headers)
    assert payment_resp.json()["status"] == "SUCCESS"