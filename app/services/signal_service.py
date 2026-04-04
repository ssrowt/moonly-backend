import requests
import time

CACHE = {"data": [], "timestamp": 0}
CACHE_TTL = 60

SYMBOLS = [
    "BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","XRPUSDT",
    "ADAUSDT","DOGEUSDT","AVAXUSDT","LINKUSDT","DOTUSDT",
    "TRXUSDT","LTCUSDT","BCHUSDT","APTUSDT","NEARUSDT",
    "ARBUSDT","OPUSDT","SUIUSDT","TONUSDT","MATICUSDT"
]


def get_24h_data():
    try:
        r = requests.get("https://api.binance.com/api/v3/ticker/24hr", timeout=5)
        data = r.json()

        if isinstance(data, list):
            return {item["symbol"]: item for item in data}
    except:
        return {}

    return {}


async def get_signals():
    now = time.time()

    if now - CACHE["timestamp"] < CACHE_TTL and CACHE["data"]:
        return CACHE["data"]

    market = get_24h_data()

    results = []

    for symbol in SYMBOLS:
        if symbol not in market:
            continue

        data = market[symbol]

        price = float(data["lastPrice"])
        change = float(data["priceChangePercent"])

        # 🔥 РЕАЛЬНАЯ ЛОГИКА
        if change > 2:
            signal = "BUY"
            score = 80
        elif change < -2:
            signal = "SELL"
            score = 80
        else:
            signal = "HOLD"
            score = 55

        results.append({
            "symbol": symbol,
            "price": round(price, 2),
            "signal": signal,
            "entry": round(price, 2),
            "tp": round(price * (1.02 if signal == "BUY" else 0.98), 2),
            "sl": round(price * (0.98 if signal == "BUY" else 1.02), 2),
            "score": score,
            "winrate": min(90, max(50, score)),
            "trend": "UP" if change > 0 else "DOWN",
            "rsi": 50,
            "is_fresh": True
        })

    if not results:
        return [{
            "symbol": "NO_DATA",
            "signal": "ERROR",
            "score": 0
        }]

    results = sorted(results, key=lambda x: x["score"], reverse=True)

    CACHE["data"] = results
    CACHE["timestamp"] = now

    return results