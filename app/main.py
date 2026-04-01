from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.services.signal_service import get_signals

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/api/signals")
def signals():
    return get_signals()