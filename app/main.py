from fastapi import FastAPI
from app.users.router import router as user_route
from app.wallets.router import router as wallet_route
from app.transfers.router import router as transfer_route
from app.payments.router import router as payment_route

app = FastAPI()
app.include_router(user_route)
app.include_router(wallet_route)
app.include_router(transfer_route)
app.include_router(payment_route)
