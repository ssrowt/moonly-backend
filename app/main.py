from fastapi import FastAPI
from app.services.signal_service import get_signals, generate_ai_analysis

app = FastAPI()


@app.get("/")
async def root():
    return {"status": "ok"}


# FREE (1 сигнал)
@app.get("/signals/free")
async def free():
    data = await get_signals()
    return data[:1]


# PRO (все сигналы)
@app.get("/signals/pro")
async def pro():
    return await get_signals()


# DELUXE (с AI)
@app.get("/signals/deluxe")
async def deluxe():
    data = await get_signals()

    for d in data:
        d["analysis"] = generate_ai_analysis(d)

    return data