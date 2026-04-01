import aiohttp
import asyncio
import time

CACHE = {
    "data": None,
    "timestamp": 0
}


async def get_top_symbols(session, limit):
    url = "https://api.binance.com/api/v3/ticker/24hr"

    async with session.get(url) as response:
        data = await response.json()

    if not isinstance(data, list):
        return []

    clean_data = [x for x in data if isinstance(x, dict)]

    sorted_data = sorted(
        clean_data,
        key=lambda x: float(x.get("quoteVolume", 0)),
        reverse=True
    )

    top_symbols = [item["symbol"] for item in sorted_data[:limit]]

    return top_symbols


async def process_symbol(session, symbol, i):
    # простая логика сигнала (потом улучшим)
    return {
        "id": i,
        "symbol": symbol,
        "price": 0,
        "support": 0,
        "resistance": 0,
        "rsi_1h": 50,
        "rsi_4h": 50,
        "signal": "SELL",
        "score": 75
    }


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

    # кеш на 10 секунд
    if now - CACHE["timestamp"] < 10:
        return CACHE["data"]

    data = asyncio.run(generate_signals())

    CACHE["data"] = data
    CACHE["timestamp"] = now

    return data