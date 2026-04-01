import aiohttp
import asyncio
import time

CACHE = {
    "data": None,
    "timestamp": 0
}

# получаем топ пары с Binance
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


# генерируем сигналы
async def generate_signals():
    async with aiohttp.ClientSession() as session:
        symbols = await get_top_symbols(session, 10)

        signals = []

        for i, symbol in enumerate(symbols):
            signals.append({
                "id": i,
                "symbol": symbol,
                "price": round(100 + i * 2, 2),
                "support": round(95 + i * 2, 2),
                "resistance": round(105 + i * 2, 2),
                "rsi_1h": 30 + i,
                "rsi_4h": 40 + i,
                "signal": "BUY" if i % 2 == 0 else "SELL",
                "score": 80 + i
            })

        return signals


# кешируем (чтобы не долбить API)
def get_mock_signals():
    now = time.time()

    if CACHE["data"] and now - CACHE["timestamp"] < 10:
        return CACHE["data"]

    data = asyncio.run(generate_signals())

    CACHE["data"] = data
    CACHE["timestamp"] = now

    return data