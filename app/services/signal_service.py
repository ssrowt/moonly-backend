import aiohttp
import asyncio
import time

CACHE = {
    "data": None,
    "timestamp": 0
}

SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT"]


async def fetch_klines(session, symbol, interval="1h", limit=100):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    async with session.get(url) as response:
        return await response.json()


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


def detect_fvg(klines):
    for i in range(2, len(klines)):
        low_prev = float(klines[i - 2][3])
        high_now = float(klines[i][2])

        if high_now < low_prev:
            return 1

        high_prev = float(klines[i - 2][2])
        low_now = float(klines[i][3])

        if low_now > high_prev:
            return 1

    return 0


async def generate_signals():
    results = []

    async with aiohttp.ClientSession() as session:
        for symbol in SYMBOLS:
            try:
                klines_1h = await fetch_klines(session, symbol, "1h")
                klines_4h = await fetch_klines(session, symbol, "4h")

                closes_1h = [float(k[4]) for k in klines_1h]
                closes_4h = [float(k[4]) for k in klines_4h]

                rsi_1h = calculate_rsi(closes_1h)
                rsi_4h = calculate_rsi(closes_4h)

                fvg = detect_fvg(klines_1h)

                price = closes_1h[-1]

                signal = "HOLD"
                score = 50

                if rsi_1h < 30 and fvg == 1:
                    signal = "BUY"
                    score = 80
                elif rsi_1h > 70 and fvg == 1:
                    signal = "SELL"
                    score = 80

                results.append({
                    "symbol": symbol,
                    "price": price,
                    "rsi_1h": round(rsi_1h, 2),
                    "rsi_4h": round(rsi_4h, 2),
                    "signal": signal,
                    "score": score,
                    "fvg": fvg
                })

            except Exception as e:
                print("ERROR:", symbol, e)

    return results


# -------- MAIN --------

async def get_signals():
    now = time.time()

    # кеш 15 секунд (важно для Render)
    if CACHE["data"] and now - CACHE["timestamp"] < 15:
        return CACHE["data"]

    try:
        data = await generate_signals()

        if not data:
            raise Exception("Empty data")

        CACHE["data"] = data
        CACHE["timestamp"] = now

        return data

    except Exception as e:
        print("FALLBACK ERROR:", e)

        # fallback (если Binance умер)
        return [
            {
                "symbol": "BTCUSDT",
                "price": 65000,
                "rsi_1h": 40,
                "rsi_4h": 45,
                "signal": "HOLD",
                "score": 50,
                "fvg": 0
            }
        ]