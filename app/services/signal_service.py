import random

COINS = [
    "BTCUSDT", "ETHUSDT", "SOLUSDT",
    "XRPUSDT", "ADAUSDT", "DOGEUSDT",
    "BNBUSDT", "AVAXUSDT", "LINKUSDT"
]

def generate_signal(symbol):
    price = round(random.uniform(50, 70000), 2)

    direction = random.choice(["LONG", "SHORT"])

    if direction == "LONG":
        entry = price
        tp = round(price * 1.02, 2)
        sl = round(price * 0.98, 2)
    else:
        entry = price
        tp = round(price * 0.98, 2)
        sl = round(price * 1.02, 2)

    return {
        "symbol": symbol,
        "signal": direction,
        "entry": entry,
        "tp": tp,
        "sl": sl,
        "trend": random.choice(["UP", "DOWN"]),
        "rsi": random.randint(30, 70),
        "winrate": random.randint(55, 70)
    }


async def get_signals():
    signals = []

    for coin in COINS:
        signals.append(generate_signal(coin))

    return signals