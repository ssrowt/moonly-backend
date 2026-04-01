import time
import asyncio

CACHE = {
    "data": None,
    "timestamp": 0
}

# ---------- TEST SIGNALS ----------
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


# ---------- SAFE ASYNC ----------
async def get_signals():
    now = time.time()

    if CACHE["data"] and now - CACHE["timestamp"] < 10:
        return CACHE["data"]

    data = await generate_signals()

    CACHE["data"] = data
    CACHE["timestamp"] = now

    return data