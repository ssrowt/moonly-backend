from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"status": "HELLO 999"}

@app.get("/signals")
def signals():
    return [{"test": "WORKING NEW CODE"}]