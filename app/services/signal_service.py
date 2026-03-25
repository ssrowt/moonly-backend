import asyncio
import aiohttp
import time

CACHE = {
    "data": [],
    "timestamp": 0
}


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.json()


async def get_top_symbols(session, limit=10):
    url = "https://api.binance.com/api/v3/ticker/24hr"
    data = await fetch(session, url)

    sorted_data = sorted(data, key=lambda x: float(x["quoteVolume"]), reverse=True)

    return [
        item["symbol"]
        for item in sorted_data
        if item["symbol"].endswith("USDT")
    ][:limit]


async def get_klines(session, symbol, interval="1h", limit=50):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    return await fetch(session, url)


def calculate_levels(klines):
    highs = [float(k[2]) for k in klines]
    lows = [float(k[3]) for k in klines]
    return min(lows), max(highs)


def calculate_rsi(klines, period=14):
    closes = [float(k[4]) for k in klines]

    gains, losses = [], []

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
    return round(100 - (100 / (1 + rs)), 2)


async def process_symbol(session, symbol, i):
    try:
        klines_1h = await get_klines(session, symbol, "1h")
        klines_4h = await get_klines(session, symbol, "4h")

        price = float(klines_1h[-1][4])

        support_1h, resistance_1h = calculate_levels(klines_1h)
        support_4h, resistance_4h = calculate_levels(klines_4h)

        rsi_1h = calculate_rsi(klines_1h)
        rsi_4h = calculate_rsi(klines_4h)

        support = min(support_1h, support_4h)
        resistance = max(resistance_1h, resistance_4h)

        signal = "WAIT"
        score = 50

        if price <= support * 1.01 and rsi_1h < 35 and rsi_4h < 40:
            signal = "BUY"
            score = 90

        elif price >= resistance * 0.99 and rsi_1h > 65 and rsi_4h > 60:
            signal = "SELL"
            score = 90

        elif rsi_1h < 30 and rsi_4h < 50:
            signal = "BUY"
            score = 75

        elif rsi_1h > 70 and rsi_4h > 55:
            signal = "SELL"
            score = 75

        return {
            "id": i + 1,
            "symbol": symbol.replace("USDT", ""),
            "price": round(price, 2),
            "support": round(support, 2),
            "resistance": round(resistance, 2),
            "rsi_1h": rsi_1h,
            "rsi_4h": rsi_4h,
            "signal": signal,
            "score": score
        }

    except Exception as e:
        print("ERROR:", symbol, e)
        return None


async def generate_signals():
    async with aiohttp.ClientSession() as session:
        symbols = await get_top_symbols(session, 15)

        tasks = [
            process_symbol(session, symbol, i)
            for i, symbol in enumerate(symbols)
        ]

        results = await asyncio.gather(*tasks)

        signals = [r for r in results if r and r["score"] >= 75]

        return signals


def get_mock_signals():
    now = time.time()

    # кэш на 10 секунд
    if now - CACHE["timestamp"] < 10:
        return CACHE["data"]

    data = asyncio.run(generate_signals())

    CACHE["data"] = data
    CACHE["timestamp"] = now

    return data