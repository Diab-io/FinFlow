from fastapi import FastAPI
from app.users.router import router as user_route
from app.wallets.router import router as wallet_route

app = FastAPI()
app.include_router(user_route)
app.include_router(wallet_route)
