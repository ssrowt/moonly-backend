from fastapi import FastAPI, Query
from services.signal_service import get_signals

app = FastAPI()


@app.get("/")
def root():
    return {"status": "MOONLY WORKING 100%"}


@app.get("/signals")
def signals(plan: str = Query("free")):
    data = get_signals()

    if not data:
        return [{"error": "NO SIGNALS"}]

    if plan == "free":
        return data[:3]

    elif plan == "pro":
        return data[:6]

    elif plan == "deluxe":
        for s in data:
            s["analysis"] = f"""
Trend: {s['trend']}
RSI: {s['rsi']}
Signal: {s['signal']}
Entry: {s['entry']}
TP: {s['tp']}
SL: {s['sl']}
Winrate: {s['winrate']}%
"""
        return data

    return data[:3]