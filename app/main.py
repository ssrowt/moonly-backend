from fastapi import FastAPI, Query
from app.services.signal_service import get_signals

app = FastAPI()


@app.get("/")
def root():
    return {"status": "WORKING"}


@app.get("/signals")
async def signals(plan: str = Query("free")):
    data = await get_signals()

    # 🔥 фильтрация
    strong = [s for s in data if s["score"] >= 80]
    medium = [s for s in data if 60 <= s["score"] < 80]
    weak = [s for s in data if s["score"] < 60]

    # 🟢 FREE — слабые сигналы (другие монеты)
    if plan == "free":
        result = weak[:5]

    # 🟡 PRO — средние сигналы
    elif plan == "pro":
        result = medium[:10]

    # 🔴 DELUXE — топ сигналы
    elif plan == "deluxe":
        result = strong[:20]

        for s in result:
            s["analysis"] = f"""
Trend: {s['trend']}
RSI: {s['rsi']}
Signal: {s['signal']}
Entry: {s['entry']}
TP: {s['tp']}
SL: {s['sl']}
Winrate: {s['winrate']}%
"""

    else:
        result = data[:5]

    # ❗ чтобы не было пусто
    if not result:
        result = data[:5]

    return result