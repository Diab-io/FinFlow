# FinFlow — Digital Wallet & Payment Processing API

A fintech backend API where users can create wallets, fund them through a payment gateway, and transfer money peer-to-peer. Every transaction uses double-entry bookkeeping for full auditability, transfers are protected by idempotency keys to prevent duplicate charges, and the system handles asynchronous payment webhooks with HMAC signature verification.

## Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Framework | FastAPI | Async-capable, auto-generated OpenAPI docs, dependency injection |
| Database | PostgreSQL + SQLAlchemy 2.0 | Industry standard relational DB with modern ORM using `Mapped` type annotations |
| Migrations | Alembic | Version-controlled schema changes |
| Caching / State | Redis | Idempotency key storage with TTL expiry |
| Auth | JWT (PyJWT) + OAuth2 | Stateless authentication with access tokens |
| Validation | Pydantic v2 | Request/response schemas with strict type enforcement |
| Containerization | Docker + Docker Compose | One-command setup: API + PostgreSQL + Redis + Mock Gateway |

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                     CLIENT (Swagger UI / Frontend)       │
└────────────────────────────┬─────────────────────────────┘
                             │ HTTPS
                             ▼
┌──────────────────────────────────────────────────────────┐
│                     FastAPI APPLICATION                   │
│                                                          │
│  ┌────────────┐ ┌────────────┐ ┌───────────┐ ┌────────┐│
│  │ Auth       │ │ Wallets    │ │ Transfers │ │Payments││
│  │ /api/auth  │ │ /api/      │ │ /api/     │ │/api/   ││
│  │            │ │ wallets    │ │ transfers │ │payments││
│  └─────┬──────┘ └─────┬──────┘ └─────┬─────┘ └───┬────┘│
│        │              │              │            │      │
│        ▼              ▼              ▼            ▼      │
│  ┌───────────────────────────────────────────────────┐   │
│  │              SERVICE LAYER                        │   │
│  │  Business logic, validation, orchestration        │   │
│  └──────────────────────┬────────────────────────────┘   │
│                         │                                │
│  ┌──────────────────────▼────────────────────────────┐   │
│  │              REPOSITORY LAYER                     │   │
│  │  Database queries via SQLAlchemy (BaseRepository) │   │
│  └───────────────────────────────────────────────────┘   │
└────────┬─────────────────┬──────────────────┬────────────┘
         │                 │                  │
         ▼                 ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌────────────────────┐
│  PostgreSQL  │  │    Redis     │  │   Mock Gateway     │
│              │  │              │  │   (port 9000)      │
│ users        │  │ idempotency  │  │                    │
│ wallets      │  │ keys w/ TTL  │  │ Simulates Paystack │
│ transactions │  │              │  │ HMAC-signed        │
│ payments     │  │              │  │ webhook callbacks  │
└──────────────┘  └──────────────┘  └────────────────────┘
```

## Project Structure

```
FinFlow/
├── app/
│   ├── auth/                      # Auth infrastructure (shared across modules)
│   │   ├── dependencies.py        # get_current_user, requires_admin
│   │   ├── security.py            # JWT creation, password hashing (bcrypt)
│   │   └── oauth2.py              # OAuth2PasswordBearer scheme
│   │
│   ├── core/                      # Shared infrastructure
│   │   ├── base_repo.py           # Generic BaseRepository with CRUD + filtering
│   │   ├── config.py              # Pydantic Settings (env vars)
│   │   ├── database.py            # SQLAlchemy engine, session, Base
│   │   ├── enums.py               # UserRole, CurrencyEnum, TransactionType, PaymentStatus
│   │   └── redis.py               # Redis client
│   │
│   ├── dtos/                      # Pydantic request/response schemas
│   │   ├── user_dto.py
│   │   ├── wallet_dto.py
│   │   ├── transfer_dto.py
│   │   ├── payment_dto.py
│   │   └── transaction_dto.py
│   │
│   ├── users/                     # User management + auth endpoints
│   │   ├── router.py              # Register, login, CRUD, role management
│   │   ├── service.py             # Registration (atomic user + wallet creation)
│   │   ├── repository.py          # User queries (by email, username)
│   │   ├── models.py              # User model with role properties
│   │   └── dependencies.py
│   │
│   ├── wallets/                   # Wallet management
│   │   ├── router.py              # GET /me, /me/balance, /me/transactions
│   │   ├── service.py             # Wallet creation, balance, paginated history
│   │   ├── repository.py          # Balance calculation, transaction queries
│   │   ├── models.py              # Wallet model
│   │   └── dependencies.py
│   │
│   ├── transfers/                 # Peer-to-peer money transfers
│   │   ├── router.py              # POST /transfers, GET /transfers/{ref}
│   │   ├── service.py             # Validation, idempotency, atomic debit+credit
│   │   └── dependencies.py
│   │
│   ├── payments/                  # Wallet funding via payment gateway
│   │   ├── router.py              # POST /fund, POST /webhook, GET /{ref}
│   │   ├── service.py             # Gateway integration, webhook handling
│   │   ├── repository.py          # Payment record queries
│   │   ├── models.py              # Payment model (tracks gateway interactions)
│   │   └── dependencies.py
│   │
│   ├── transactions/              # Ledger (no router — internal data layer)
│   │   ├── models.py              # Transaction model (the double-entry ledger)
│   │   └── repository.py          # Transaction queries by reference
│   │
│   ├── main.py                    # FastAPI app with router registration
│   └── migrations/                # Alembic migration versions
│
├── mock_gateway/                  # Simulates external payment processor
│   └── main.py                    # POST /charge with HMAC-signed callback
│
├── tests/
│   ├── conftest.py                # Fixtures: test DB, client, auth, wallet funding
│   ├── test_auth.py               # Registration, login, validation, duplicates
│   ├── test_wallets.py            # Wallet creation, balance, currency selection
│   ├── test_transfers.py          # Transfers, idempotency, validation, edge cases
│   └── test_payments.py           # Funding, webhooks, signatures, full flow
│
├── docker-compose.yml             # API + PostgreSQL + Redis
├── Dockerfile
├── makefile                       # Migration shortcuts
├── requirements.txt
└── README.md
```

## Key Features

**Double-Entry Bookkeeping** — Every money movement creates paired transaction records. Transfers produce a debit on the sender's wallet and a credit on the receiver's wallet, sharing the same reference. Wallet balances are calculated from the sum of all credits minus debits, never stored directly. This ensures a complete audit trail and makes it impossible to lose money to partial operations.

**Idempotent Transfers** — Clients send an `X-Idempotency-Key` header with every transfer request. Before processing, the service checks Redis for that key. If found, the original response is returned without re-executing the transfer. Keys expire after 24 hours. This prevents double charges from network retries or duplicate submissions.

**Async Payment Webhooks** — Wallet funding follows the real-world payment flow: the API initiates a charge with the mock gateway, returns a pending status immediately, and the gateway calls back via a webhook when processing completes. The webhook payload is signed with HMAC-SHA256 so the API can verify authenticity before crediting the wallet.

**Mock Payment Gateway** — A separate FastAPI application that simulates a payment processor like Paystack. It receives charge requests, randomly simulates success (80%) or failure (20%), signs the response payload with a shared secret, and calls the main API's webhook endpoint. Swapping to a real provider would only require changing the gateway adapter.

**Atomic Operations** — User registration creates both the user and wallet in a single database transaction using the `commit=False` pattern. If wallet creation fails, the user creation rolls back too. The same pattern protects transfers — both the debit and credit entries are committed together or not at all.

**Role-Based Access Control** — Three roles (customer, merchant, admin) with endpoint-level enforcement via FastAPI dependencies. Admin-only endpoints use a `requires_admin` dependency that checks the user's role before the handler runs.

## API Endpoints

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register a new user (auto-creates wallet) |
| POST | `/api/auth/token` | Login and receive JWT access token |
| GET | `/api/auth/users` | List all users (admin only) |
| GET | `/api/auth/users/{id}` | Get user by ID |
| PATCH | `/api/auth/users/{id}` | Update user profile |
| PATCH | `/api/auth/users/{id}/role` | Change user role (admin only) |

### Wallets
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/wallets/me` | Get current user's wallet details |
| GET | `/api/wallets/me/balance` | Get calculated balance |
| GET | `/api/wallets/me/transactions` | Paginated transaction history |

### Transfers
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/transfers/` | Send money to another wallet (requires `X-Idempotency-Key` header) |
| GET | `/api/transfers/{reference}` | Get transfer details by reference |

### Payments
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/payments/fund` | Initiate wallet funding via payment gateway |
| POST | `/api/payments/webhook` | Webhook callback from payment gateway (no auth, HMAC verified) |
| GET | `/api/payments/{reference}` | Check payment status |

## Database Design

```
users
  id          UUID (PK)
  username    str (unique)
  email       str (unique)
  password    str (hashed)
  phone       str (optional)
  role        enum: admin | merchant | customer
  active      bool
  created_at  datetime
  updated_at  datetime

wallets
  id              UUID (PK)
  user_id         UUID (FK → users, unique)
  account_number  str(10) (unique, auto-generated)
  currency        enum: NGN | USD | GBP | EUR | JPY
  created_at      datetime
  -- balance is CALCULATED, not stored

transactions (the ledger)
  id          UUID (PK)
  wallet_id   UUID (FK → wallets)
  type        enum: CREDIT | DEBIT
  amount      decimal(15,2)
  reference   str (groups related entries)
  description str (optional)
  created_at  datetime

payments (gateway interaction tracking)
  id                UUID (PK)
  user_id           UUID (FK → users)
  amount            decimal(15,2)
  status            enum: PENDING | SUCCESS | FAILED
  reference         str (unique)
  gateway_response  JSON (raw webhook payload)
  created_at        datetime
```

## Setup & Installation

### Prerequisites
- Docker & Docker Compose
- Git

### Running the System

```bash
# Clone the repo
git clone https://github.com/Diab-io/FinFlow.git
cd FinFlow

# Create .env file
cp .env.example .env
# Edit .env with your values

# Start all services (API + PostgreSQL + Redis + Mock Gateway)
docker-compose up --build

# Run database migrations
make upgrade

# View API docs
# Main API: http://localhost:8000/docs
# Mock Gateway: http://localhost:9000/docs
```

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@db:5432/finflow` |
| `TEST_DATABASE_URL` | Test database connection string | `postgresql://user:pass@db:5432/finflow_test` |
| `POSTGRES_DB` | Database name | `finflow` |
| `POSTGRES_USER` | Database user | `postgres` |
| `POSTGRES_PASSWORD` | Database password | `postgres` |
| `JWT_SECRET_KEY` | Secret for signing JWTs | `your-secret-key` |
| `JWT_ALGORITHM` | JWT signing algorithm | `HS256` |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiry | `30` |
| `WEBHOOK_KEY` | Shared secret for HMAC webhook signatures | `your-webhook-secret` |
| `REDIS_HOST` | Redis hostname | `redis` |
| `REDIS_PORT` | Redis port | `6379` |

### Running Tests

```bash
# Run all tests
docker exec -it finflow-api pytest

# Run with verbose output
docker exec -it finflow-api pytest -v

# Run specific test file
docker exec -it finflow-api pytest tests/test_transfers.py -v
```

## Example Flows

### Fund Wallet
```
POST /api/payments/fund  →  Payment created (PENDING)
                         →  Charge request sent to mock gateway
                         →  Gateway processes and calls POST /api/payments/webhook
                         →  Webhook verified (HMAC) → wallet credited → payment status: SUCCESS
```

### Transfer Money
```
POST /api/transfers/  →  Idempotency key checked in Redis
                      →  Sender balance verified
                      →  Currency match verified
                      →  Debit entry created on sender's wallet
                      →  Credit entry created on receiver's wallet
                      →  Both committed atomically
                      →  Result cached in Redis with idempotency key (24h TTL)
```

## What I'd Improve

- **Cached balance on wallet model** — Currently balance is recalculated from full transaction history on every request. A production version would maintain a cached balance updated atomically alongside each transaction, with periodic reconciliation against the ledger.
- **Combine balance query into single SQL** — The current implementation uses two separate queries (credits and debits). A single query with CASE expressions would halve the database round trips.
- **Strict double-entry for external funding** — Currently wallet funding creates a single credit entry. A production system would add a platform settlement account as the counter-party for complete ledger reconciliation.
- **Celery background workers** — Add async task processing for email notifications on transfers, scheduled report generation, and retry logic for failed webhook deliveries.
- **OpenTelemetry tracing** — Add distributed tracing for request observability across the API, database, and Redis.
- **Rate limiting** — Add Redis-backed rate limiting middleware on auth and transfer endpoints.
- **Account closure workflow** — Implement a multi-step account closure process with balance verification and final settlement.
- **Merchant API keys** — Add API key authentication for merchants to accept payments programmatically, with per-key rate limiting and usage analytics.
- **CI/CD pipeline** — GitHub Actions workflow to run tests and linting on every push.
- **Database read replicas** — Route reporting and history queries to read replicas to reduce load on the primary database.

## License

MIT