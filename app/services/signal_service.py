import aiohttp
import asyncio
import time

CACHE = {
    "data": None,
    "timestamp": 0
}

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

    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period

    if avg_loss == 0:
        return 100

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


# ---------- FVG ----------
def detect_fvg(candles):
    zones = []

    for i in range(2, len(candles)):
        prev = candles[i - 2]
        curr = candles[i]

        high_prev = float(prev[2])
        low_prev = float(prev[3])
        high_curr = float(curr[2])
        low_curr = float(curr[3])

        # bullish gap
        if low_curr > high_prev:
            zones.append("bullish")

        # bearish gap
        if high_curr < low_prev:
            zones.append("bearish")

    return zones


# ---------- Binance ----------
async def get_top_symbols(session, limit=10):
    url = "https://api.binance.com/api/v3/ticker/24hr"

    async with session.get(url) as response:
        data = await response.json()

    sorted_data = sorted(
        data,
        key=lambda x: float(x.get("quoteVolume", 0)),
        reverse=True
    )

    symbols = [
        x["symbol"]
        for x in sorted_data
        if x["symbol"].endswith("USDT")
    ]

    return symbols[:limit]


async def get_klines(session, symbol, interval):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit=100"

    async with session.get(url) as response:
        return await response.json()


# ---------- LOGIC ----------
async def process_symbol(session, symbol, i):
    try:
        klines_1h = await get_klines(session, symbol, "1h")
        klines_4h = await get_klines(session, symbol, "4h")

        closes_1h = [float(k[4]) for k in klines_1h]
        closes_4h = [float(k[4]) for k in klines_4h]

        rsi_1h = calculate_rsi(closes_1h)
        rsi_4h = calculate_rsi(closes_4h)

        fvg = detect_fvg(klines_1h)

        price = closes_1h[-1]

        signal = "WAIT"
        score = 50

        # RSI логика
        if rsi_1h < 35 and rsi_4h < 40:
            signal = "BUY"
            score = 85

        elif rsi_1h > 65 and rsi_4h > 60:
            signal = "SELL"
            score = 85

        # FVG усиливает сигнал
        if fvg:
            score += 5

        return {
            "id": i,
            "symbol": symbol,
            "price": round(price, 4),
            "rsi_1h": round(rsi_1h, 2),
            "rsi_4h": round(rsi_4h, 2),
            "signal": signal,
            "score": score,
            "fvg": len(fvg)
        }

    except Exception:
        return None


# ---------- GENERATOR ----------
async def generate_signals():
    async with aiohttp.ClientSession() as session:
        symbols = await get_top_symbols(session, 10)

        tasks = [
            process_symbol(session, symbol, i)
            for i, symbol in enumerate(symbols)
        ]

        results = await asyncio.gather(*tasks)

        signals = [r for r in results if r is not None]

        if not signals:
            return generate_test_signals()

        return signals


# ---------- FALLBACK ----------
def generate_test_signals():
    return [
        {
            "id": i,
            "symbol": f"TEST{i}",
            "price": 100 + i,
            "rsi_1h": 30,
            "rsi_4h": 40,
            "signal": "BUY" if i % 2 == 0 else "SELL",
            "score": 90,
            "fvg": 1
        }
        for i in range(5)
    ]


# ---------- MAIN ----------
async def get_signals():
    now = time.time()

    if CACHE["data"] and now - CACHE["timestamp"] < 15:
        return CACHE["data"]

    data = await generate_signals()

    CACHE["data"] = data
    CACHE["timestamp"] = now

    return data