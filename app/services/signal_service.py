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


# 📊 RSI
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


# 🎯 FVG (упрощённый)
def detect_fvg(highs, lows):
    if len(highs) < 3:
        return 0

    if lows[-1] > highs[-3]:
        return 1   # bullish imbalance
    elif highs[-1] < lows[-3]:
        return -1  # bearish imbalance

    return 0


# 🧠 SCORE (качество сигнала)
def calculate_score(rsi, fvg):
    score = 50

    if rsi < 35:
        score += 20
    elif rsi > 65:
        score += 20

    if fvg != 0:
        score += 20

    return min(score, 95)


# 📈 Winrate (оценка)
def estimate_winrate(score):
    return min(50 + (score - 50), 90)


# 🚀 ОСНОВА
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
            highs = [float(x[2]) for x in data if len(x) > 2]
            lows = [float(x[3]) for x in data if len(x) > 3]

            if len(closes) < 30:
                continue

            price = closes[-1]
            rsi = calculate_rsi(closes)
            fvg = detect_fvg(highs, lows)

            signal = "HOLD"

            if rsi < 35 and fvg == 1:
                signal = "BUY"
            elif rsi > 65 and fvg == -1:
                signal = "SELL"

            # 📊 уровни
            entry = price

            if signal == "BUY":
                sl = price * 0.98
                tp = price * 1.05
            elif signal == "SELL":
                sl = price * 1.02
                tp = price * 0.95
            else:
                sl = price
                tp = price

            score = calculate_score(rsi, fvg)
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
                "fvg": fvg,
                "is_fresh": True
            })

        except Exception as e:
            print("ERROR:", symbol, e)

    # 🔥 сортировка по качеству
    results = sorted(results, key=lambda x: x["score"], reverse=True)

    CACHE["data"] = results
    CACHE["timestamp"] = now

    return results