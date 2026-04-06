import random

COINS = [
    "BTCUSDT","ETHUSDT","SOLUSDT",
    "XRPUSDT","ADAUSDT","DOGEUSDT",
    "BNBUSDT","AVAXUSDT","LINKUSDT"
]

def get_signals():
    signals = []

    for coin in COINS:
        price = round(random.uniform(100, 70000), 2)

        direction = random.choice(["LONG", "SHORT"])

        if direction == "LONG":
            tp = round(price * 1.02, 2)
            sl = round(price * 0.98, 2)
        else:
            tp = round(price * 0.98, 2)
            sl = round(price * 1.02, 2)

        signals.append({
            "symbol": coin,
            "signal": direction,
            "entry": price,
            "tp": tp,
            "sl": sl,
            "trend": random.choice(["UP", "DOWN"]),
            "rsi": random.randint(30, 70),
            "winrate": random.randint(55, 70)
        })

    return signals