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


def detect_impulse(closes):
    return (closes[-1] - closes[-5]) / closes[-5]


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


def is_strong_signal(rsi, impulse):
    if impulse < 0.003:
        return False
    if 45 < rsi < 55:
        return False
    return True


def calculate_levels(data, signal, fvg_zone):
    highs = [float(x[2]) for x in data[-20:]]
    lows = [float(x[3]) for x in data[-20:]]

    recent_high = max(highs)
    recent_low = min(lows)

    if not fvg_zone:
        return None, None, None

    zone_type, zone_low, zone_high = fvg_zone

    if signal == "BUY" and zone_type == "bullish":
        return round(zone_low,2), round(recent_high,2), round(recent_low,2)

    if signal == "SELL" and zone_type == "bearish":
        return round(zone_high,2), round(recent_low,2), round(recent_high,2)

    return None, None, None


def update_history(signal):
    signal["id"] = str(uuid.uuid4())
    signal["timestamp"] = int(time.time())
    signal["result"] = "OPEN"
    HISTORY.append(signal)

    if len(HISTORY) > 50:
        HISTORY.pop(0)


async def get_signals():
    now = time.time()

    if now - CACHE["timestamp"] < CACHE_TTL and CACHE["data"]:
        return CACHE["data"]

    results = []
    fallback = []

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

            # fallback сигнал (ВСЕГДА)
            basic_signal = "BUY" if rsi < 50 else "SELL"

            fallback.append({
                "symbol": symbol,
                "price": round(price, 2),
                "signal": basic_signal,
                "entry": round(price,2),
                "tp": round(price * (1.02 if basic_signal == "BUY" else 0.98),2),
                "sl": round(price * (0.98 if basic_signal == "BUY" else 1.02),2),
                "score": 50,
                "winrate": 50,
                "trend": trend,
                "rsi": round(rsi, 2),
                "is_fresh": True
            })

            # сильные сигналы
            if not is_strong_signal(rsi, impulse):
                continue

            signal = None

            if rsi < 40 and trend == "UP":
                signal = "BUY"

            elif rsi > 60 and trend == "DOWN":
                signal = "SELL"

            if not signal:
                continue

            entry, tp, sl = calculate_levels(data, signal, fvg_zone)

            if not entry:
                continue

            score = int(abs(impulse) * 1000)
            score = max(60, min(90, score))
            winrate = min(90, max(50, score - 5))

            signal_data = {
                "symbol": symbol,
                "price": round(price, 2),
                "signal": signal,
                "entry": entry,
                "tp": tp,
                "sl": sl,
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

    # если нет сильных → fallback
    if not results:
        results = fallback

    results = sorted(results, key=lambda x: x["score"], reverse=True)

    CACHE["data"] = results
    CACHE["timestamp"] = now

    return results


@app.get("/")
def root():
    return {"status": "MOONLY FINAL LIVE"}


@app.get("/signals")
async def signals(plan: str = Query("free")):
    data = await get_signals()

    if plan == "free":
        result = data[:5]

    elif plan == "pro":
        result = data[:10]

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

    else:
        result = data[:5]

    return result


@app.get("/history")
def history():
    return HISTORY[::-1]