from fastapi import FastAPI, Query
from app.services.signal_service import get_signals

app = FastAPI()


@app.get("/")
def root():
    return {"status": "MOONLY MVP 🚀"}


@app.get("/signals")
async def signals(plan: str = Query("free")):
    data = await get_signals()

    if plan == "free":
        result = data[:5]

    elif plan == "pro":
        result = data[:10]

    elif plan == "deluxe":
        result = data[:20]

        for s in result:
            s["analysis"] = f"""
Signal: {s['signal']}
Entry: {s['entry']}
TP: {s['tp']}
SL: {s['sl']}
Winrate: {s['winrate']}%
"""

    else:
        result = data[:5]

    return result