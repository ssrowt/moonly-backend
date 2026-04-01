from fastapi import FastAPI, Query
from app.services.signal_service import get_signals

app = FastAPI()


@app.get("/")
def root():
    return {"status": "WORKING"}


@app.get("/signals")
async def signals(plan: str = Query("free")):
    data = await get_signals()

    if plan == "free":
        return data[:3]

    elif plan == "pro":
        pro = [s for s in data if s["signal"] != "HOLD"]
        return pro[:5] if pro else data[:5]

    elif plan == "deluxe":
        deluxe = [
            s for s in data
            if s["signal"] != "HOLD" and s["score"] >= 60
        ]

        if not deluxe:
            deluxe = data[:5]

        for s in deluxe:
            s["analysis"] = generate_analysis(s)

        return deluxe[:5]

    return data


def generate_analysis(s):
    if s["signal"] == "BUY":
        return f"Bullish setup. Entry {s['entry']}."
    elif s["signal"] == "SELL":
        return f"Bearish setup. Entry {s['entry']}."
    return "Weak setup."