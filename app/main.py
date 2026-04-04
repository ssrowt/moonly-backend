from fastapi import FastAPI, Query
from app.services.signal_service import get_signals

app = FastAPI()


@app.get("/")
def root():
    return {"status": "WORKING REAL SYSTEM"}


@app.get("/signals")
async def signals(plan: str = Query("free")):
    data = await get_signals()

    # 🔥 ЖЁСТКОЕ РАЗДЕЛЕНИЕ

    if plan == "free":
        result = data[10:15]

    elif plan == "pro":
        result = data[5:15]

    elif plan == "deluxe":
        result = data[:20]

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

    if not result:
        result = data[:5]

    return result