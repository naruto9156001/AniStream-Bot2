from datetime import datetime

from fastapi import APIRouter, HTTPException

from app.database import progress, series, episodes

router = APIRouter(
    prefix="/api/v1/progress",
    tags=["Progress"]
)


@router.get("/")
async def get_progress():

    total_series = series.count_documents({})
    total_episodes = episodes.count_documents({})

    completed = progress.count_documents(
        {"status": "completed"}
    )

    running = progress.count_documents(
        {"status": "running"}
    )

    pending = progress.count_documents(
        {"status": "pending"}
    )

    failed = progress.count_documents(
        {"status": "failed"}
    )

    return {
        "success": True,
        "summary": {
            "total_series": total_series,
            "total_episodes": total_episodes,
            "completed": completed,
            "running": running,
            "pending": pending,
            "failed": failed
        }
    }


@router.get("/{anime_slug}")
async def anime_progress(anime_slug: str):

    data = progress.find_one(
        {"anime_slug": anime_slug},
        {"_id": 0}
    )

    if not data:
        raise HTTPException(
            status_code=404,
            detail="Progress not found."
        )

    return {
        "success": True,
        "progress": data
    }


@router.post("/start/{anime_slug}")
async def start_job(
    anime_slug: str,
    total_episodes: int
):

    progress.update_one(
        {
            "anime_slug": anime_slug
        },
        {
            "$set": {
                "anime_slug": anime_slug,
                "status": "running",
                "total_episodes": total_episodes,
                "saved_episodes": 0,
                "last_episode_saved": 0,
                "updated_at": datetime.utcnow()
            }
        },
        upsert=True
    )

    return {
        "success": True,
        "message": "Job Started"
    }


@router.post("/update/{anime_slug}/{episode}")
async def update_progress(
    anime_slug: str,
    episode: int
):

    progress.update_one(
        {
            "anime_slug": anime_slug
        },
        {
            "$set": {
                "saved_episodes": episode,
                "last_episode_saved": episode,
                "updated_at": datetime.utcnow()
            }
        }
    )

    return {
        "success": True
    }


@router.post("/complete/{anime_slug}")
async def complete_job(
    anime_slug: str
):

    progress.update_one(
        {
            "anime_slug": anime_slug
        },
        {
            "$set": {
                "status": "completed",
                "updated_at": datetime.utcnow()
            }
        }
    )

    return {
        "success": True,
        "message": "Completed"
    }


@router.post("/failed/{anime_slug}")
async def failed_job(
    anime_slug: str
):

    progress.update_one(
        {
            "anime_slug": anime_slug
        },
        {
            "$set": {
                "status": "failed",
                "updated_at": datetime.utcnow()
            }
        }
    )

    return {
        "success": True,
        "message": "Failed"
    }
