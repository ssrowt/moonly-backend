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


def safe_request(url):
    try:
        r = requests.get(url, timeout=5)
        data = r.json()

        # ❗ если Binance дал ошибку
        if isinstance(data, dict):
            return None

        return data
    except:
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


async def get_signals():
    now = time.time()

    if now - CACHE["timestamp"] < CACHE_TTL and CACHE["data"]:
        return CACHE["data"]

    results = []

    for symbol in SYMBOLS:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=15m&limit=100"
        data = safe_request(url)

        if not data or len(data) < 60:
            continue

        closes = [float(x[4]) for x in data]
        price = closes[-1]

        rsi = calculate_rsi(closes)
        trend = get_trend(closes)

        # 🔥 РЕАЛЬНЫЙ РАЗНООБРАЗНЫЙ СИГНАЛ
        if rsi < 35 and trend == "UP":
            signal = "BUY"
            score = 80
        elif rsi > 65 and trend == "DOWN":
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
            "trend": trend,
            "rsi": round(rsi, 2),
            "is_fresh": True
        })

        # ❗ анти бан Binance
        time.sleep(0.2)

    # ❗ если всё равно пусто
    if not results:
        return [{
            "symbol": "ERROR",
            "signal": "NO DATA",
            "score": 0
        }]

    results = sorted(results, key=lambda x: x["score"], reverse=True)

    CACHE["data"] = results
    CACHE["timestamp"] = now

    return results