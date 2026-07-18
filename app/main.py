from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.config import APP_NAME, APP_VERSION
from app.database import init_database

# Routers
# (Abhi ye files nahi bani hain,
# isliye abhi comment me rakhe hain.)

# from app.api.series import router as series_router
# from app.api.episodes import router as episodes_router
# from app.api.search import router as search_router
# from app.api.progress import router as progress_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting AnimeSalt Backend...")
    init_database()
    print("✅ Backend Ready")
    yield
    print("🛑 Backend Stopped")


app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="AnimeSalt Production Backend",
    lifespan=lifespan
)


@app.get("/")
async def root():
    return {
        "status": "ok",
        "backend": APP_NAME,
        "version": APP_VERSION
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy"
    }


@app.get("/ping")
async def ping():
    return {
        "message": "pong"
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": str(exc)
        }
    )


# Register Routers
#
# app.include_router(series_router)
# app.include_router(episodes_router)
# app.include_router(search_router)
# app.include_router(progress_router)
