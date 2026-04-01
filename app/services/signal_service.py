import requests
import pandas as pd
import time

CACHE = {
    "data": [],
    "timestamp": 0
}


# 📊 RSI
def calculate_rsi(series, period=14):
    delta = series.diff()

    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

    rs = gain / loss
    return 100 - (100 / (1 + rs))


# ⚡ FVG (упрощенный)
def detect_fvg(df):
    fvg_list = []

    for i in range(2, len(df)):
        if df["low"][i] > df["high"][i - 2]:
            fvg_list.append(1)
        else:
            fvg_list.append(0)

    return [0, 0] + fvg_list


# 🚀 ОСНОВНАЯ ФУНКЦИЯ
async def get_signals():
    now = time.time()

    # ⚡ КЕШ
    if now - CACHE["timestamp"] < 120:
        return CACHE["data"]

    symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT"]

    signals = []

    try:
        for symbol in symbols:
            url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1h&limit=100"
            data = requests.get(url).json()

            df = pd.DataFrame(data)
            df.columns = [
                "time", "open", "high", "low", "close", "volume",
                "_", "_", "_", "_", "_", "_"
            ]

            df["close"] = df["close"].astype(float)
            df["high"] = df["high"].astype(float)
            df["low"] = df["low"].astype(float)

            # RSI
            df["rsi"] = calculate_rsi(df["close"])

            # FVG
            df["fvg"] = detect_fvg(df)

            last = df.iloc[-1]

            signal = "HOLD"

            if last["rsi"] < 35 and last["fvg"] == 1:
                signal = "BUY"
            elif last["rsi"] > 65:
                signal = "SELL"

            signals.append({
                "symbol": symbol,
                "price": round(last["close"], 2),
                "rsi": round(last["rsi"], 2),
                "signal": signal,
                "score": int(100 - abs(50 - last["rsi"])),
                "fvg": int(last["fvg"])
            })

        # сортировка
        signals = sorted(signals, key=lambda x: x["score"], reverse=True)

        # кеш
        CACHE["data"] = signals
        CACHE["timestamp"] = now

        return signals

    except Exception as e:
        print("ERROR:", e)

        if CACHE["data"]:
            return CACHE["data"]

        return []