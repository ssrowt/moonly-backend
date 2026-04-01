import aiohttp
import asyncio
import time

CACHE = {
    "data": None,
    "timestamp": 0
}

SYMBOLS = [
    "BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT",
    "BNBUSDT", "ADAUSDT", "DOGEUSDT"
]


# ---------- RSI ----------
def calculate_rsi(closes, period=14):
    gains = []
    losses = []

    for i in range(1, len(closes)):
        diff = closes[i] - closes[i - 1]
        if diff >= 0:
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


# ---------- FVG ----------
def detect_fvg(klines):
    for i in range(2, len(klines)):
        low_prev = float(klines[i - 2][3])
        high_now = float(klines[i][2])

        if high_now < low_prev:
            return 1  # bearish

        high_prev = float(klines[i - 2][2])
        low_now = float(klines[i][3])

        if low_now > high_prev:
            return 1  # bullish

    return 0


# ---------- API ----------
async def fetch_klines(session, symbol, interval):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit=100"
    async with session.get(url, timeout=10) as response:
        return await response.json()


# ---------- CORE ----------
async def process_symbol(session, symbol):
    try:
        klines_1h = await fetch_klines(session, symbol, "1h")
        klines_4h = await fetch_klines(session, symbol, "4h")

        if not klines_1h or not klines_4h:
            return None

        closes_1h = [float(k[4]) for k in klines_1h]
        closes_4h = [float(k[4]) for k in klines_4h]

        rsi_1h = calculate_rsi(closes_1h)
        rsi_4h = calculate_rsi(closes_4h)

        fvg = detect_fvg(klines_1h)
        price = closes_1h[-1]

        signal = "HOLD"
        score = 0

        # ---------- ЛОГИКА 10/10 ----------
        if rsi_1h < 30 and rsi_4h < 40 and fvg == 1:
            signal = "BUY"
            score = 90

        elif rsi_1h > 70 and rsi_4h > 60 and fvg == 1:
            signal = "SELL"
            score = 90

        # фильтр слабых
        if signal == "HOLD":
            return None

        return {
            "symbol": symbol,
            "price": round(price, 4),
            "rsi_1h": round(rsi_1h, 2),
            "rsi_4h": round(rsi_4h, 2),
            "signal": signal,
            "score": score,
            "fvg": fvg
        }

    except Exception as e:
        print("ERROR:", symbol, e)
        return None


# ---------- GENERATE ----------
async def generate_signals():
    async with aiohttp.ClientSession() as session:
        tasks = [process_symbol(session, s) for s in SYMBOLS]
        results = await asyncio.gather(*tasks)

        signals = [r for r in results if r]

        # сортировка по силе
        signals.sort(key=lambda x: x["score"], reverse=True)

        # оставляем топ 3
        return signals[:3]


# ---------- MAIN ----------
async def get_signals():
    now = time.time()

    # кеш 15 сек
    if CACHE["data"] and now - CACHE["timestamp"] < 15:
        return CACHE["data"]

    try:
        data = await generate_signals()

        if not data:
            raise Exception("No signals")

        CACHE["data"] = data
        CACHE["timestamp"] = now

        return data

    except Exception as e:
        print("FALLBACK:", e)

        return [
            {
                "symbol": "BTCUSDT",
                "price": 65000,
                "rsi_1h": 50,
                "rsi_4h": 50,
                "signal": "HOLD",
                "score": 0,
                "fvg": 0
            }
        ]