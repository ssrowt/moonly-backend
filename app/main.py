from fastapi import FastAPI
from app.services.signal_service import get_signals

app = FastAPI()


@app.get("/")
async def root():
    return {"status": "ok"}


@app.get("/signals")
async def signals():
    return await get_signals()