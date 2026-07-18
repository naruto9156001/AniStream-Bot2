from fastapi import APIRouter
from app.database import series, episodes, progress

router = APIRouter(
    prefix="/api/v1/progress",
    tags=["Progress"]
)


@router.get("/")
async def get_progress():

    total_series = series.count_documents({})
    total_episodes = episodes.count_documents({})

    completed = progress.count_documents({
        "status": "completed"
    })

    running = progress.count_documents({
        "status": "running"
    })

    failed = progress.count_documents({
        "status": "failed"
    })

    pending = progress.count_documents({
        "status": "pending"
    })

    return {
        "success": True,
        "summary": {
            "series": total_series,
            "episodes": total_episodes,
            "completed": completed,
            "running": running,
            "failed": failed,
            "pending": pending
        }
    }


@router.get("/{anime_slug}")
async def anime_progress(anime_slug: str):

    data = progress.find_one(
        {"anime_slug": anime_slug},
        {"_id": 0}
    )

    if not data:
        return {
            "success": False,
            "message": "Anime not found."
        }

    return {
        "success": True,
        "progress": data
    }
