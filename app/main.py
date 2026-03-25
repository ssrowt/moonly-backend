from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.services.signal_service import get_mock_signals

app = FastAPI(title="Moonly API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Moonly backend is running"}

@app.get("/signals")
def get_signals():
    return get_mock_signals()