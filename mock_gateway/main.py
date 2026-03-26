import hmac
import hashlib
import random
import os
import requests
import json
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel, HttpUrl

load_dotenv()

app = FastAPI(title="Mock Payment Gateway")

class ChargeRequest(BaseModel):
    reference: str
    amount: float
    callback_url: HttpUrl

@app.post('/charge')
def charge(data: ChargeRequest):
    secret = os.getenv("WEBHOOK_KEY")

    if not secret:
        raise ValueError("WEBHOOK_KEY is not set")

    callback_url = data.callback_url  # <-- extract BEFORE reassigning

    response_data = {
        "reference": data.reference
    }

    if random.random() > 0.2:
        response_data.update({"status": "success"})
    else:
        response_data.update({"status": "failed", "reason": "Card declined"})

    encoded_payload = json.dumps(response_data).encode()
    hmac_signature = hmac.new(
        secret.encode(),
        encoded_payload,
        hashlib.sha256
    ).hexdigest()

    print("----------Calling:", callback_url)
    requests.post(str(callback_url), json=response_data, headers={
        "x-webhook-signature": hmac_signature
    })

    return {"received": True}

