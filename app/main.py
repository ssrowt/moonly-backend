from fastapi import FastAPI, Query
from app.services.signal_service import get_signals

app = FastAPI()


@app.get("/")
def root():
    return {"status": "WORKING"}


@app.get("/signals")
async def signals(plan: str = Query("free")):
    data = await get_signals()

    # 🔥 делим по силе
    strong = [s for s in data if s["score"] >= 70]
    medium = [s for s in data if 50 <= s["score"] < 70]
    weak = [s for s in data if s["score"] < 50]

    # 🟢 FREE — слабые + немного средних
    if plan == "free":
        result = weak + medium[:2]

        if not result:
            result = data[:3]

        return result[:3]

    # 🟡 PRO — средние + немного сильных
    elif plan == "pro":
        result = medium + strong[:2]

        if not result:
            result = data[:5]

        return result[:5]

    # 🔴 DELUXE — только сильные
    elif plan == "deluxe":
        result = strong

        if not result:
            result = data[:5]

        for s in result:
            s["analysis"] = generate_analysis(s)

        return result[:5]

    return data


def generate_analysis(s):
    if s["signal"] == "BUY":
        return f"Strong bullish setup. Entry {s['entry']}."
    elif s["signal"] == "SELL":
        return f"Strong bearish setup. Entry {s['entry']}."
    return "Weak market."