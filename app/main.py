from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"status": "SUPER_WORKING_123"}

@app.get("/signals")
def signals():
    return [
        {"coin": "TEST1"},
        {"coin": "TEST2"}
    ]