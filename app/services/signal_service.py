import requests
import time

CACHE = {"data": [], "timestamp": 0}
CACHE_TTL = 60

SYMBOLS = [
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT",
    "ADAUSDT", "DOGEUSDT", "AVAXUSDT", "LINKUSDT", "DOTUSDT",
    "TRXUSDT", "LTCUSDT", "BCHUSDT", "APTUSDT", "NEARUSDT",
    "ARBUSDT", "OPUSDT", "SUIUSDT", "TONUSDT", "MATICUSDT"
]


def calculate_rsi(closes, period=14):
    gains, losses = [], []

    for i in range(1, len(closes)):
        diff = closes[i] - closes[i - 1]
        gains.append(max(diff, 0))
        losses.append(abs(min(diff, 0)))

    if len(gains) < period:
        return 50

    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period

    if avg_loss == 0:
        return 100

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def calculate_score(rsi):
    return int(100 - abs(50 - rsi))


def estimate_winrate(score):
    return min(50 + (score - 50), 90)


async def get_signals():
    now = time.time()

    if now - CACHE["timestamp"] < CACHE_TTL:
        return CACHE["data"]

    results = []

    for symbol in SYMBOLS:
        try:
            url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=15m&limit=100"
            response = requests.get(url, timeout=5)

            if response.status_code != 200:
                continue

            data = response.json()

            if not isinstance(data, list) or len(data) == 0:
                continue

            closes = [float(x[4]) for x in data if len(x) > 4]

            if len(closes) < 30:
                continue

            price = closes[-1]
            rsi = calculate_rsi(closes)

            # 🔥 ВСЕГДА есть сигнал
            if rsi < 45:
                signal = "BUY"
            elif rsi > 55:
                signal = "SELL"
            else:
                signal = "HOLD"

            entry = price

            if signal == "BUY":
                sl = price * 0.98
                tp = price * 1.04
            elif signal == "SELL":
                sl = price * 1.02
                tp = price * 0.96
            else:
                sl = price * 0.99
                tp = price * 1.01

            score = calculate_score(rsi)
            winrate = estimate_winrate(score)

            results.append({
                "symbol": symbol,
                "price": round(price, 2),
                "signal": signal,
                "rsi": round(rsi, 2),
                "entry": round(entry, 2),
                "sl": round(sl, 2),
                "tp": round(tp, 2),
                "score": score,
                "winrate": winrate,
                "is_fresh": True
            })

        except Exception as e:
            print("ERROR:", symbol, e)

    results = sorted(results, key=lambda x: x["score"], reverse=True)

    CACHE["data"] = results
    CACHE["timestamp"] = now

    return results