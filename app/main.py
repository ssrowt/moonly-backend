from fastapi import FastAPI, Query
from app.services.signal_service import get_signals

app = FastAPI()


@app.get("/")
def root():
    return {"status": "MOONLY BACKEND LIVE 🚀"}


@app.get("/signals")
async def signals(plan: str = Query("free")):
    data = await get_signals()

    # 🔥 РАЗДЕЛЕНИЕ ПО ПОДПИСКАМ

    if plan == "free":
        result = data[:5]

    elif plan == "pro":
        result = data[:10]

    elif plan == "deluxe":
        result = data[:20]

        # AI-анализ только в deluxe
        for s in result:
            s["analysis"] = (
                f"Trend: {s['trend']} | "
                f"RSI: {s['rsi']} | "
                f"Impulse: {round(s['impulse'], 4)} | "
                f"Signal: {s['signal']} | "
                f"Entry: {s['entry']} | "
                f"TP: {s['tp']} | "
                f"SL: {s['sl']} | "
                f"Winrate: {s['winrate']}%"
            )

    else:
        result = data[:5]

    return result