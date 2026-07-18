from math import ceil

from fastapi import APIRouter, HTTPException, Query

from app.database import episodes
from app.config import DEFAULT_LIMIT, MAX_LIMIT

router = APIRouter(
    prefix="/api/v1/episodes",
    tags=["Episodes"]
)


@router.get("/{anime_slug}")
async def get_episode_list(
    anime_slug: str,
    page: int = Query(1, ge=1),
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=MAX_LIMIT)
):

    query = {
        "anime_slug": anime_slug
    }

    total = episodes.count_documents(query)

    data = list(
        episodes.find(
            query,
            {"_id": 0}
        )
        .sort("episode", 1)
        .skip((page - 1) * limit)
        .limit(limit)
    )

    return {
        "success": True,
        "anime_slug": anime_slug,
        "page": page,
        "limit": limit,
        "total": total,
        "pages": ceil(total / limit) if total else 0,
        "results": data
    }


@router.get("/{anime_slug}/{episode}")
async def get_episode(
    anime_slug: str,
    episode: int
):

    data = episodes.find_one(
        {
            "anime_slug": anime_slug,
            "episode": episode
        },
        {
            "_id": 0
        }
    )

    if not data:
        raise HTTPException(
            status_code=404,
            detail="Episode not found."
        )

    previous_episode = episodes.find_one(
        {
            "anime_slug": anime_slug,
            "episode": episode - 1
        },
        {
            "_id": 0,
            "episode": 1,
            "title": 1
        }
    )

    next_episode = episodes.find_one(
        {
            "anime_slug": anime_slug,
            "episode": episode + 1
        },
        {
            "_id": 0,
            "episode": 1,
            "title": 1
        }
    )

    return {
        "success": True,
        "episode": data,
        "navigation": {
            "previous": previous_episode,
            "next": next_episode
        }
    }


@router.get("/id/{episode_id}")
async def get_episode_by_id(
    episode_id: str
):

    data = episodes.find_one(
        {
            "episode_id": episode_id
        },
        {
            "_id": 0
        }
    )

    if not data:
        raise HTTPException(
            status_code=404,
            detail="Episode not found."
        )

    return {
        "success": True,
        "episode": data
    }
