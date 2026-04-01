import time

CACHE = {
    "data": None,
    "timestamp": 0
}

async def generate_signals():
    signals = []

    for i in range(10):
        signals.append({
            "id": i,
            "symbol": f"TEST{i}",
            "price": 100 + i,
            "rsi_1h": 30,
            "rsi_4h": 40,
            "signal": "BUY" if i % 2 == 0 else "SELL",
            "score": 90
        })

    return signals


def get_signals():
    import asyncio

    now = time.time()

    if CACHE["data"] and now - CACHE["timestamp"] < 10:
        return CACHE["data"]

    data = asyncio.run(generate_signals())

    CACHE["data"] = data
    CACHE["timestamp"] = now

    return data