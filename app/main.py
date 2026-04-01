from fastapi import FastAPI, Query
from app.services.signal_service import get_signals

app = FastAPI()


@app.get("/")
def root():
    return {"status": "WORKING"}


@app.get("/signals")
async def signals(plan: str = Query("free")):
    data = await get_signals()

    # 🟢 FREE
    if plan == "free":
        return data[:3]

    # 🟡 PRO
    elif plan == "pro":
        pro = [
            s for s in data
            if s["signal"] != "HOLD" and s["score"] >= 60
        ]

        if not pro:
            pro = data[:5]

        return pro[:5]

    # 🔴 DELUXE
    elif plan == "deluxe":
        deluxe = [
            s for s in data
            if s["signal"] != "HOLD" and s["score"] >= 75
        ]

        if not deluxe:
            deluxe = data[:5]

        for s in deluxe:
            s["analysis"] = generate_analysis(s)

        return deluxe[:5]

    return data


def generate_analysis(s):
    if s["signal"] == "BUY":
        return f"Strong bullish setup. Entry {s['entry']}."
    elif s["signal"] == "SELL":
        return f"Strong bearish pressure. Entry {s['entry']}."
    return "Weak setup."