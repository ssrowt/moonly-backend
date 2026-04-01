from fastapi import FastAPI, Query
from app.services.signal_service import get_signals

app = FastAPI()


@app.get("/")
def root():
    return {"status": "WORKING"}


@app.get("/signals")
async def signals(plan: str = Query("free")):
    data = await get_signals()

    # 🟢 FREE — любые сигналы
    if plan == "free":
        return data[:3]

    # 🟡 PRO — только BUY / SELL
    elif plan == "pro":
        pro = [s for s in data if s["signal"] != "HOLD"]

        if len(pro) < 3:
            return data[:5]

        return pro[:5]

    # 🔴 DELUXE — топ сигналы
    elif plan == "deluxe":
        deluxe = [
            s for s in data
            if s["signal"] != "HOLD" and s["score"] >= 65
        ]

        # 💥 если нет — fallback
        if len(deluxe) < 3:
            deluxe = sorted(
                [s for s in data if s["signal"] != "HOLD"],
                key=lambda x: x["score"],
                reverse=True
            )

        deluxe = deluxe[:5]

        for s in deluxe:
            s["analysis"] = generate_analysis(s)

        return deluxe

    return data


def generate_analysis(s):
    if s["signal"] == "BUY":
        return f"Market shows bullish momentum. Entry {s['entry']}."
    elif s["signal"] == "SELL":
        return f"Bearish structure detected. Entry {s['entry']}."
    return "Weak setup."