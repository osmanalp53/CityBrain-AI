from fastapi import FastAPI

app = FastAPI(title="CityBrain AI", version="0.1.0")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}