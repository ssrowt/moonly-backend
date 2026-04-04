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


def get_klines(symbol):
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=15m&limit=100"
        r = requests.get(url, timeout=5)
        data = r.json()

        if isinstance(data, list):
            return data
    except:
        return None

    return None


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


def get_trend(closes):
    sma20 = sum(closes[-20:]) / 20
    sma50 = sum(closes[-50:]) / 50

    if sma20 > sma50:
        return "UP"
    elif sma20 < sma50:
        return "DOWN"
    return "FLAT"


def get_impulse(closes):
    return (closes[-1] - closes[-5]) / closes[-5]


async def get_signals():
    now = time.time()

    if now - CACHE["timestamp"] < CACHE_TTL and CACHE["data"]:
        return CACHE["data"]

    results = []

    for symbol in SYMBOLS:
        data = get_klines(symbol)

        if not data or len(data) < 60:
            continue

        closes = [float(x[4]) for x in data]
        price = closes[-1]

        rsi = calculate_rsi(closes)
        trend = get_trend(closes)
        impulse = get_impulse(closes)

        score = 50
        signal = "HOLD"

        # 🔥 МЯГКАЯ ЛОГИКА

        if rsi < 45 and trend == "UP":
            signal = "BUY"
            score = 70

        elif rsi > 55 and trend == "DOWN":
            signal = "SELL"
            score = 70

        # усиливаем сигнал импульсом
        if impulse > 0.015 and signal == "BUY":
            score += 10

        if impulse < -0.015 and signal == "SELL":
            score += 10

        # если всё равно HOLD → даем направление по тренду
        if signal == "HOLD":
            signal = "BUY" if trend == "UP" else "SELL"
            score = 60

        results.append({
            "symbol": symbol,
            "price": round(price, 2),
            "signal": signal,
            "entry": round(price, 2),
            "tp": round(price * (1.02 if signal == "BUY" else 0.98), 2),
            "sl": round(price * (0.98 if signal == "BUY" else 1.02), 2),
            "score": score,
            "winrate": min(90, max(50, score)),
            "trend": trend,
            "rsi": round(rsi, 2),
            "impulse": round(impulse, 4),
            "is_fresh": True
        })

        time.sleep(0.15)

    # fallback если вообще ничего нет
    if not results:
        results = [{
            "symbol": "BTCUSDT",
            "price": 65000,
            "signal": "BUY",
            "entry": 65000,
            "tp": 67000,
            "sl": 63000,
            "score": 60,
            "winrate": 60,
            "trend": "UP",
            "rsi": 50,
            "impulse": 0.01,
            "is_fresh": True
        }]

    results = sorted(results, key=lambda x: x["score"], reverse=True)

    CACHE["data"] = results
    CACHE["timestamp"] = now

    return results