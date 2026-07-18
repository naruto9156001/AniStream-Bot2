from fastapi import APIRouter, Query
from app.database import series

router = APIRouter(
    prefix="/api/v1/search",
    tags=["Search"]
)


@router.get("/")
async def search_anime(
    q: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=100)
):

    query = {
        "$or": [
            {
                "title": {
                    "$regex": q,
                    "$options": "i"
                }
            },
            {
                "slug": {
                    "$regex": q,
                    "$options": "i"
                }
            },
            {
                "genres": {
                    "$regex": q,
                    "$options": "i"
                }
            }
        ]
    }

    results = list(
        series.find(
            query,
            {
                "_id": 0
            }
        ).limit(limit)
    )

    return {
        "success": True,
        "query": q,
        "count": len(results),
        "results": results
    }


@router.get("/suggest")
async def suggestions(
    q: str = Query(..., min_length=1)
):

    data = list(
        series.find(
            {
                "title": {
                    "$regex": q,
                    "$options": "i"
                }
            },
            {
                "_id": 0,
                "title": 1,
                "slug": 1
            }
        ).limit(10)
    )

    return {
        "success": True,
        "suggestions": data
    }
