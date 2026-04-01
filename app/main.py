from fastapi import FastAPI, Query
from app.services.signal_service import get_signals

app = FastAPI(title="Moonly API")


@app.get("/")
async def root():
    return {"status": "ok"}


@app.get("/signals")
async def signals(plan: str = Query("free")):
    data = await get_signals()

    # 🟢 FREE — топ 5
    if plan == "free":
        symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT"]
        return [s for s in data if s["symbol"] in symbols][:2]

    # 🟡 PRO — топ 10
    elif plan == "pro":
        symbols = [
            "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT",
            "ADAUSDT", "DOGEUSDT", "AVAXUSDT", "LINKUSDT", "DOTUSDT"
        ]
        return [s for s in data if s["symbol"] in symbols][:6]

    # 🔴 DELUXE — топ 20 + топ сигналы
    elif plan == "deluxe":
        symbols = [
            "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT",
            "ADAUSDT", "DOGEUSDT", "AVAXUSDT", "LINKUSDT", "DOTUSDT