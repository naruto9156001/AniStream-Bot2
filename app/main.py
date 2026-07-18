from fastapi import FastAPI

app = FastAPI(
    title="AnimeSalt Backend",
    description="AnimeSalt API v1.0",
    version="1.0.0"
)


@app.get("/")
async def root():
    return {
        "status": "ok",
        "name": "AnimeSalt Backend",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy"
    }
