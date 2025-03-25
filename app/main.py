from fastapi import FastAPI
from app.proxy_handler import proxy_router

app = FastAPI()
app.include_router(proxy_router)
