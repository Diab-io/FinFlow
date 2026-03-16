#  FinFlow — Digital Wallet & Payment Processing API


## Overview

A fintech API where users can create wallets, fund them through a payment
gateway, transfer money peer-to-peer, and merchants can accept payments via API
keys. Every transaction uses double-entry bookkeeping for auditability, transfers are idempotent so no double charges happen, and the system handles async payment webhooks with retry logic.

## Tech Stack

- **Framework:** Python, FastAPI
- **Database:** Postgres, SQLAlchemy 2.0
- **Migrations:** alembic
- **Caching:** Redis
- **Task Queue:** Celery + Redis broker
- **Auth:** JWT (pythonjose) + OAuth2
- **Validation:** Pydantic v2
- **Containerization:** Docker + dockercompose
