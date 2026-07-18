from math import ceil

from fastapi import APIRouter, HTTPException, Query

from app.database import series
from app.config import DEFAULT_LIMIT, MAX_LIMIT

router = APIRouter(
    prefix="/api/v1/series",
    tags=["Series"]
)


@router.get("/")
async def get_series(
    page: int = Query(1, ge=1),
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
    search: str | None = None,
    sort: str = "title"
):
    query = {}

    if search:
        query["title"] = {
            "$regex": search,
            "$options": "i"
        }

    sort_map = {
        "title": [("title", 1)],
        "latest": [("updated_at", -1)],
        "oldest": [("updated_at", 1)]
    }

    sort_order = sort_map.get(
        sort,
        [("title", 1)]
    )

    total = series.count_documents(query)

    data = list(
        series.find(
            query,
            {"_id": 0}
        )
        .sort(sort_order)
        .skip((page - 1) * limit)
        .limit(limit)
    )

    return {
        "success": True,
        "page": page,
        "limit": limit,
        "total": total,
        "pages": ceil(total / limit) if total else 0,
        "results": data
    }


@router.get("/{slug}")
async def get_series_by_slug(slug: str):

    anime = series.find_one(
        {"slug": slug},
        {"_id": 0}
    )

    if not anime:
        raise HTTPException(
            status_code=404,
            detail="Anime not found."
        )

    return {
        "success": True,
        "data": anime
    }
