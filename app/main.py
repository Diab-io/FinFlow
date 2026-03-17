from fastapi import FastAPI
from app.users.router import router as user_route

app = FastAPI()
app.include_router(user_route)
