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
        symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT"]
        result = [s for s in data if s["symbol"] in symbols]
        return sorted(result, key=lambda x: x["score"], reverse=True)[:2]

    # 🟡 PRO
    elif plan == "pro":
        symbols = [
            "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT",
            "ADAUSDT", "DOGEUSDT", "AVAXUSDT", "LINKUSDT", "DOTUSDT"
        ]
        result = [s for s in data if s["symbol"] in symbols]
        return sorted(result, key=lambda x: x["score"], reverse=True)[:6]

    # 🔴 DELUXE
    elif plan == "deluxe":
        symbols = [
            "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT",
            "ADAUSDT", "DOGEUSDT", "AVAXUSDT", "LINKUSDT", "DOTUSDT",
            "TRXUSDT", "LTCUSDT", "BCHUSDT", "APTUSDT", "NEARUSDT",
            "ARBUSDT", "OPUSDT", "SUIUSDT", "TONUSDT", "MATICUSDT"
        ]

        result = [s for s in data if s["symbol"] in symbols]

        # 🔥 всегда есть сигналы
        result = sorted(result, key=lambda x: x["score"], reverse=True)[:8]

        for s in result:
            s["analysis"] = generate_analysis(s)

        return result

    return data


def generate_analysis(s):
    if s["signal"] == "BUY":
        return f"Market looks bullish. Entry {s['entry']} with upside potential."
    elif s["signal"] == "SELL":
        return f"Bearish pressure detected. Possible drop from {s['entry']}."
    return "Weak market structure, low confidence."