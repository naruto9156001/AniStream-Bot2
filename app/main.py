from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import APP_NAME, APP_VERSION
from app.database import init_database

from app.api.series import router as series_router
from app.api.episodes import router as episodes_router
from app.api.search import router as search_router
from app.api.progress import router as progress_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("=" * 60)
    print("🚀 Starting AnimeSalt Backend")
    print("=" * 60)

    init_database()

    print("✅ MongoDB Connected")
    print("✅ Backend Ready")
    print("=" * 60)

    yield

    print("=" * 60)
    print("🛑 Backend Stopped")
    print("=" * 60)


app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="AnimeSalt Production Backend",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Root"])
async def root():
    return {
        "success": True,
        "name": APP_NAME,
        "version": APP_VERSION,
        "status": "online"
    }


@app.get("/health", tags=["Health"])
async def health():
    return {
        "success": True,
        "status": "healthy"
    }


@app.get("/ping", tags=["Health"])
async def ping():
    return {
        "message": "pong"
    }


app.include_router(series_router)
app.include_router(episodes_router)
app.include_router(search_router)
app.include_router(progress_router)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": str(exc)
        }
    )
