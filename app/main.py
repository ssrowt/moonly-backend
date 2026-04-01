from fastapi import FastAPI, Query
from app.services.signal_service import get_signals

app = FastAPI()


@app.get("/")
async def root():
    return {"status": "ok"}


@app.get("/signals")
async def signals(plan: str = Query("free")):
    data = await get_signals()

    # 💰 PAYWALL ЛОГИКА
    if plan == "free":
        return data[:2]

    elif plan == "pro":
        return data[:10]

    elif plan == "deluxe":
        return data  # + потом добавим AI

    return data