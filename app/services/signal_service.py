import requests
import pandas as pd
import time

CACHE = {
    "data": [],
    "timestamp": 0
}

CACHE_TTL = 90


ALL_SYMBOLS = [
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT",
    "ADAUSDT", "DOGEUSDT", "TONUSDT", "AVAXUSDT", "LINKUSDT",
    "MATICUSDT", "DOTUSDT", "TRXUSDT", "LTCUSDT", "BCHUSDT",
    "APTUSDT", "NEARUSDT", "ARBUSDT", "OPUSDT", "SUIUSDT"
]


# 📊 RSI
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()

    rs = gain / loss
    return 100 - (100 / (1 + rs))


# 📊 ATR
def calculate_atr(df, period=14):
    high_low = df["high"] - df["low"]
    high_close = abs(df["high"] - df["close"].shift())
    low_close = abs(df["low"] - df["close"].shift())

    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)

    return true_range.rolling(period).mean()


# ⚡ FVG
def detect_fvg(df):
    fvg = [0, 0]

    for i in range(2, len(df)):
        if df["low"][i] > df["high"][i - 2]:
            fvg.append(1)
        elif df["high"][i] < df["low"][i - 2]:
            fvg.append(-1)
        else:
            fvg.append(0)

    return fvg


# 🎯 winrate оценка
def estimate_winrate(rsi, fvg):
    score = 50

    if rsi < 30:
        score += 20
    elif rsi > 70:
        score += 15

    if fvg != 0:
        score += 15

    return min(score, 95)


# 🚀 ОСНОВА
async def get_signals():
    now = time.time()

    if now - CACHE["timestamp"] < CACHE_TTL:
        return CACHE["data"]

    signals = []

    try:
        for symbol in ALL_SYMBOLS:
            url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=15m&limit=150"
            data = requests.get(url, timeout=10).json()

            df = pd.DataFrame(data)
            df.columns = [
                "time", "open", "high", "low", "close", "volume",
                "_", "_", "_", "_", "_", "_"
            ]

            df["close"] = df["close"].astype(float)
            df["high"] = df["high"].astype(float)
            df["low"] = df["low"].astype(float)

            df["rsi"] = calculate_rsi(df["close"])
            df["atr"] = calculate_atr(df)
            df["fvg"] = detect_fvg(df)

            last = df.iloc[-1]

            signal = "HOLD"

            if last["rsi"] < 35 and last["fvg"] == 1:
                signal = "BUY"
            elif last["rsi"] > 65 and last["fvg"] == -1:
                signal = "SELL"

            price = last["close"]
            atr = last["atr"]

            if signal == "BUY":
                entry = price
                sl = price - atr * 1.5
                tp = price + atr * 3

            elif signal == "SELL":
                entry = price
                sl = price + atr * 1.5
                tp = price - atr * 3

            else:
                entry = price
                sl = price
                tp = price

            score = int((100 - abs(50 - last["rsi"])) + (10 if last["fvg"] != 0 else 0))

            winrate = estimate_winrate(last["rsi"], last["fvg"])

            age = int(now - (last["time"] / 1000))

            signals.append({
                "symbol": symbol,
                "price": round(price, 2),
                "signal": signal,
                "rsi": round(last["rsi"], 2),
                "entry": round(entry, 2),
                "sl": round(sl, 2),
                "tp": round(tp, 2),
                "score": score,
                "winrate": winrate,
                "fvg": int(last["fvg"]),
                "age_sec": age,
                "is_fresh": age < 900
            })

        signals = sorted(signals, key=lambda x: x["score"], reverse=True)

        CACHE["data"] = signals
        CACHE["timestamp"] = now

        return signals

    except Exception as e:
        print("ERROR:", e)

        if CACHE["data"]:
            return CACHE["data"]

        return []