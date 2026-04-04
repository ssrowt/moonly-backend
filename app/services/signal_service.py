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

        signal = "HOLD"
        score = 50

        # 🔥 BUY логика
        if (
            rsi < 40
            and trend == "UP"
            and impulse > 0.01
        ):
            signal = "BUY"
            score = 85

        # 🔥 SELL логика
        elif (
            rsi > 60
            and trend == "DOWN"
            and impulse < -0.01
        ):
            signal = "SELL"
            score = 85

        # слабые сигналы
        elif rsi < 35:
            signal = "BUY"
            score = 65

        elif rsi > 65:
            signal = "SELL"
            score = 65

        if signal == "HOLD":
            continue  # ❗ фильтр — не показываем мусор

        results.append({
            "symbol": symbol,
            "price": round(price, 2),
            "signal": signal,
            "entry": round(price, 2),
            "tp": round(price * (1.03 if signal == "BUY" else 0.97), 2),
            "sl": round(price * (0.97 if signal == "BUY" else 1.03), 2),
            "score": score,
            "winrate": min(90, max(50, score)),
            "trend": trend,
            "rsi": round(rsi, 2),
            "impulse": round(impulse, 4),
            "is_fresh": True
        })

        time.sleep(0.2)

    # fallback
    if not results:
        results = [{
            "symbol": "NO SIGNALS",
            "signal": "WAIT",
            "score": 0
        }]

    results = sorted(results, key=lambda x: x["score"], reverse=True)

    CACHE["data"] = results
    CACHE["timestamp"] = now

    return results