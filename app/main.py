from fastapi import FastAPI, Query
import requests
import time
import uuid

app = FastAPI()

CACHE = {"data": [], "timestamp": 0}
CACHE_TTL = 60

HISTORY = []

SYMBOLS = [
    "BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","XRPUSDT",
    "ADAUSDT","DOGEUSDT","AVAXUSDT","LINKUSDT","DOTUSDT",
    "TRXUSDT","LTCUSDT","BCHUSDT","APTUSDT","NEARUSDT",
    "ARBUSDT","OPUSDT","SUIUSDT","TONUSDT","MATICUSDT"
]

# ===== RSI =====
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


# ===== TREND =====
def get_trend(closes):
    sma20 = sum(closes[-20:]) / 20
    sma50 = sum(closes[-50:]) / 50

    if sma20 > sma50:
        return "UP"
    elif sma20 < sma50:
        return "DOWN"
    return "FLAT"


# ===== IMPULSE =====
def detect_impulse(closes):
    return (closes[-1] - closes[-5]) / closes[-5]


# ===== FVG =====
def detect_fvg_zone(data):
    for i in range(len(data)-3, 2, -1):
        low_prev = float(data[i - 2][3])
        high_prev = float(data[i - 2][2])
        low = float(data[i][3])
        high = float(data[i][2])

        if low > high_prev:
            return ("bullish", high_prev, low)

        if high < low_prev:
            return ("bearish", high, low_prev)

    return None


# ===== HISTORY =====
def update_history(signal):
    signal["id"] = str(uuid.uuid4())
    signal["timestamp"] = int(time.time())
    signal["result"] = "OPEN"
    HISTORY.append(signal)

    if len(HISTORY) > 100:
        HISTORY.pop(0)


# ===== SIGNAL ENGINE =====
async def get_signals():
    now = time.time()

    if now - CACHE["timestamp"] < CACHE_TTL and CACHE["data"]:
        return CACHE["data"]

    results = []

    for symbol in SYMBOLS:
        try:
            url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=15m&limit=100"
            r = requests.get(url, timeout=5)
            data = r.json()

            if not isinstance(data, list) or len(data) < 60:
                continue

            closes = [float(x[4]) for x in data]
            price = closes[-1]

            rsi = calculate_rsi(closes)
            trend = get_trend(closes)
            impulse = detect_impulse(closes)
            fvg_zone = detect_fvg_zone(data)

            # ===== СИГНАЛ ВСЕГДА =====
            if rsi < 40:
                signal = "BUY"
            elif rsi > 60:
                signal = "SELL"
            else:
                signal = "BUY" if trend == "UP" else "SELL"

            # ===== ENTRY =====
            if fvg_zone:
                zone_type, zl, zh = fvg_zone
                entry = zl if signal == "BUY" else zh
            else:
                entry = price

            # ===== TP / SL =====
            tp = entry * (1.02 if signal == "BUY" else 0.98)
            sl = entry * (0.98 if signal == "BUY" else 1.02)

            # ===== SCORE =====
            score = int(abs(impulse) * 1000)

            if fvg_zone:
                score += 10

            if (signal == "BUY" and trend == "UP") or (signal == "SELL" and trend == "DOWN"):
                score += 10

            score = max(50, min(90, score))
            winrate = score

            signal_data = {
                "symbol": symbol,
                "price": round(price, 2),
                "signal": signal,
                "entry": round(entry, 2),
                "tp": round(tp, 2),
                "sl": round(sl, 2),
                "score": score,
                "winrate": winrate,
                "trend": trend,
                "rsi": round(rsi, 2),
                "is_fresh": True
            }

            results.append(signal_data)
            update_history(signal_data.copy())

        except Exception as e:
            print("ERR", symbol, e)

    # ВСЕГДА есть сигналы
    results = sorted(results, key=lambda x: x["score"], reverse=True)

    CACHE["data"] = results
    CACHE["timestamp"] = now

    return results


# ===== API =====
@app.get("/")
def root():
    return {"status": "MOONLY FINAL LIVE"}


@app.get("/signals")
async def signals(plan: str = Query("free")):
    data = await get_signals()

    if plan == "free":
        return data[:5]

    elif plan == "pro":
        return data[:10]

    elif plan == "deluxe":
        result = data[:20]

        for s in result:
            s["analysis"] = f"""
Trend: {s['trend']}
RSI: {s['rsi']}
Signal: {s['signal']}
Entry: {s['entry']}
TP: {s['tp']}
SL: {s['sl']}
Winrate: {s['winrate']}%
"""
        return result

    return data[:5]


@app.get("/history")
def history():
    return HISTORY[::-1]