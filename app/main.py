from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def root():
    return {"status": "WORKING"}


@app.get("/signals")
def signals():
    return [
        {
            "symbol": "BTCUSDT",
            "signal": "BUY",
            "entry": 65000,
            "tp": 67000,
            "sl": 63000,
            "winrate": 72
        },
        {
            "symbol": "ETHUSDT",
            "signal": "SELL",
            "entry": 3200,
            "tp": 3000,
            "sl": 3350,
            "winrate": 68
        }
    ]