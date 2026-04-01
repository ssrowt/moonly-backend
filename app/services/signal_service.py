import requests
import time

CACHE = {
    "data": [],
    "timestamp": 0
}

CACHE_TTL = 60

SYMBOLS = [
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT",
    "ADAUSDT", "DOGEUSDT", "AVAXUSDT", "LINKUSDT", "DOTUSDT",
    "TRXUSDT", "LTCUSDT", "BCHUSDT", "APTUSDT", "NEARUSDT",
    "ARBUSDT", "OPUSDT", "SUIUSDT", "TONUSDT", "MATICUSDT"
]


def calculate_rsi(closes, period=14):
    gains = []
    losses = []

    for i in range(1, len(closes)):
        diff = closes[i] - closes[i - 1]
        if diff > 0:
            gains.append(diff)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(diff))

    if len(gains) < period:
        return 50

    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period

    if avg_loss == 0:
        return 100

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def estimate_winrate(rsi):
    return min(50 + abs(50 - rsi), 90)


async def get_signals():
    now = time.time()

    if now - CACHE["timestamp"] < CACHE_TTL:
        return CACHE["data"]

    results = []

    for symbol in SYMBOLS:
        try:
            url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=15m&limit=50"
            response = requests.get(url, timeout=5)

            if response.status_code != 200:
                print("BAD RESPONSE:", symbol)
                continue

            data = response.json()

            if not isinstance(data, list) or len(data) == 0:
                print("BAD DATA:", symbol, data)
                continue

            closes = [float(x[4]) for x in data if len(x) > 4]

            if len(closes) < 20:
                continue

            price = closes[-1]
            rsi = calculate_rsi(closes)

            signal = "HOLD"

            if rsi < 35:
                signal = "BUY"
            elif rsi > 65:
                signal = "SELL"

            entry = price

            if signal == "BUY":
                sl = price * 0.98
                tp = price * 1.04
            elif signal == "SELL":
                sl = price * 1.02
                tp = price * 0.96
            else:
                sl = price
                tp = price

            score = int(100 - abs(50 - rsi))
            winrate = estimate_winrate(rsi)

            results.append({
                "symbol": symbol,
                "price": round(price, 2),
                "signal": signal,
                "rsi": round(rsi, 2),
                "entry": round(entry, 2),
                "sl": round(sl, 2),
                "tp": round(tp, 2),
                "score": score,
                "winrate": int(winrate),
                "is_fresh": True
            })

        except Exception as e:
            print("ERROR:", symbol, e)

    results = sorted(results, key=lambda x: x["score"], reverse=True)

    CACHE["data"] = results
    CACHE["timestamp"] = now

    return results