import os
import asyncio
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import APP_NAME, APP_VERSION
from app.database import Database          # <-- New database class
from app.scraper.crawler import Crawler    # <-- New crawler

from app.api.series import router as series_router
from app.api.episodes import router as episodes_router
from app.api.search import router as search_router
from app.api.progress import router as progress_router
from app.api.upload import router as upload_router
from app.api.animesalt import router as animesalt_router   # <-- New router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("=" * 60)
    print("🚀 Starting AnimeSalt Backend")
    print("=" * 60)

    # MongoDB connection (already handled inside Database class)
    db = Database()
    print("✅ MongoDB Connected")

    # Start background scraper
    asyncio.create_task(background_scraper())

    print("✅ Backend Ready")
    print("=" * 60)
    yield
    print("=" * 60)
    print("🛑 Backend Stopped")
    print("=" * 60)


async def background_scraper():
    """Background scraper - runs full scan at configured interval"""
    interval_minutes = int(os.getenv("BG_PROCESS_DURATION", 60))  # Default 60 minutes
    interval_seconds = interval_minutes * 60

    crawler = Crawler()  # Instantiate once

    while True:
        try:
            print(f"🔄 Auto Scraper started at {datetime.utcnow()} (every {interval_minutes} min)")
            # Run the full scan
            crawler.run_full_scan()
            print("✅ Auto Scraper completed")
        except Exception as e:
            print(f"❌ Scraper error: {e}")
        await asyncio.sleep(interval_seconds)


# FastAPI app
app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="AnimeSalt Production Backend",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoints
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
    return {"message": "pong"}

# Register routers
app.include_router(series_router)
app.include_router(episodes_router)
app.include_router(search_router)
app.include_router(progress_router)
app.include_router(upload_router)
app.include_router(animesalt_router)   # <-- New router added

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": str(exc)
        }
    )
