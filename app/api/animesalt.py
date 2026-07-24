from fastapi import APIRouter, Query
from app.scraper.runner import ScraperRunner

router = APIRouter()
runner = ScraperRunner()

@router.get("/animesalt/episode")
async def get_episode(url: str = Query(..., description="Episode URL")):
    try:
        data = runner.get_episode(url)
        return {"status": "success", "data": data}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.get("/animesalt/series/{series_id}/episodes")
async def get_series_episodes(
    series_id: str,
    season: int = Query(None, description="Filter by season")
):
    try:
        url = f"https://animesalt.link/series/{series_id}/"
        data = runner.get_series_episodes(url, season)
        return {"status": "success", "data": data}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.get("/animesalt/search")
async def search_anime(query: str = Query(..., description="Search query")):
    try:
        data = runner.search(query)
        return {"status": "success", "data": data}
    except Exception as e:
        return {"status": "error", "message": str(e)}
