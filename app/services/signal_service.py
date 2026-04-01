import aiohttp
import asyncio
import time

CACHE = {
    "data": None,
    "timestamp": 0
}

async def get_top_symbols(session, limit=10):
    url = "https://api.binance.com/api/v3/ticker/24hr"

    async with session.get(url) as response:
        data = await response.json()

    if not isinstance(data, list):
        return []

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


async def generate_signals():
    async with aiohttp.ClientSession() as session:
        symbols = await get_top_symbols(session, 10)

        signals = []

        for i, symbol in enumerate(symbols):
            signals.append({
                "id": i,
                "symbol": symbol,
                "price": 0,
                "support": 0,
                "resistance": 0,
                "rsi_1h": 50,
                "rsi_4h": 50,
                "signal": "BUY" if i % 2 == 0 else "SELL",
                "score": 70 + i
            })

        return signals


def get_mock_signals():
    now = time.time()

    if now - CACHE["timestamp"] < 10:
        return CACHE["data"]

    data = asyncio.run(generate_signals())

    CACHE["data"] = data
    CACHE["timestamp"] = now

    return data