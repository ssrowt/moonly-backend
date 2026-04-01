from fastapi import FastAPI, Query
from app.services.signal_service import get_signals

app = FastAPI()


@app.get("/")
def root():
    return {"status": "WORKING"}


@app.get("/signals")
async def signals(plan: str = Query("free")):
    data = await get_signals()

    strong = [s for s in data if s["score"] >= 70]
    medium = [s for s in data if 50 <= s["score"] < 70]
    weak = [s for s in data if s["score"] < 50]

    # FREE
    if plan == "free":
        result = (weak + medium)[:5]

    # PRO
    elif plan == "pro":
        result = (medium + strong)[:10]

    # DELUXE
    elif plan == "deluxe":
        result = strong[:20]

        for s in result:
            s["analysis"] = f"{s['signal']} setup. Entry {s['entry']}, TP {s['tp']}, SL {s['sl']}"

    else:
        result = data[:5]

    # ❗ ГАРАНТИЯ: не будет []
    if not result:
        result = data[:5]

    return result