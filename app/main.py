from fastapi import FastAPI, Query
from app.services.signal_service import get_signals

app = FastAPI(title="Moonly API")


@app.get("/")
async def root():
    return {"status": "ok"}


@app.get("/signals")
async def signals(plan: str = Query("free")):
    data = await get_signals()

    # 🟢 FREE — топ 5
    if plan == "free":
        symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT"]
        return [s for s in data if s["symbol"] in symbols][:2]

    # 🟡 PRO — топ 10
    elif plan == "pro":
        symbols = [
            "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT",
            "ADAUSDT", "DOGEUSDT", "TONUSDT", "AVAXUSDT", "LINKUSDT"
        ]
        return [s for s in data if s["symbol"] in symbols][:6]

    # 🔴 DELUXE — топ 20 + только сильные сигналы
    elif plan == "deluxe":
        symbols = [
            "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT",
            "ADAUSDT", "DOGEUSDT", "TONUSDT", "AVAXUSDT", "LINKUSDT",
            "MATICUSDT", "DOTUSDT", "TRXUSDT", "LTCUSDT", "BCHUSDT",
            "APTUSDT", "NEARUSDT", "ARBUSDT", "OPUSDT", "SUIUSDT"
        ]

        # 🔥 фильтр ТОП сигналов
        result = [
            s for s in data
            if s["symbol"] in symbols and s["score"] >= 80 and s["signal"] != "HOLD"
        ]

        for s in result:
            s["analysis"] = generate_analysis_text(s)

        return result

    return data


def generate_analysis_text(signal):
    if signal["signal"] == "BUY":
        return f"Bullish momentum. Entry near {signal['entry']} with upside potential."
    elif signal["signal"] == "SELL":
        return f"Bearish setup. Possible drop from {signal['entry']}."
    return "Market unclear."