import os
import requests

class TMDBClient:
    def __init__(self):
        self.api_key = os.getenv("TMDB_API_KEY")
        self.base = "https://api.themoviedb.org/3"
        self.image_base = "https://image.tmdb.org/t/p/w500"
        
    def search_series(self, title: str):
        """Search TMDB for a series by title."""
        url = f"{self.base}/search/tv"
        params = {"api_key": self.api_key, "query": title}
        resp = requests.get(url, params=params)
        if resp.status_code == 200:
            results = resp.json().get("results", [])
            return results[0] if results else None
        return None

    def get_series_details(self, tmdb_id: int):
        url = f"{self.base}/tv/{tmdb_id}"
        params = {"api_key": self.api_key}
        resp = requests.get(url, params=params)
        if resp.status_code == 200:
            return resp.json()
        return None

    def get_season_details(self, tmdb_id: int, season_num: int):
        url = f"{self.base}/tv/{tmdb_id}/season/{season_num}"
        params = {"api_key": self.api_key}
        resp = requests.get(url, params=params)
        if resp.status_code == 200:
            return resp.json()
        return None

    def get_episode_details(self, tmdb_id: int, season_num: int, episode_num: int):
        url = f"{self.base}/tv/{tmdb_id}/season/{season_num}/episode/{episode_num}"
        params = {"api_key": self.api_key}
        resp = requests.get(url, params=params)
        if resp.status_code == 200:
            return resp.json()
        return None

    def enrich_series(self, series_data: dict):
        """Add TMDB poster/backdrop to series data."""
        tmdb = self.search_series(series_data["title"])
        if tmdb:
            series_data["tmdb_id"] = tmdb["id"]
            series_data["poster"] = f"{self.image_base}{tmdb['poster_path']}" if tmdb.get("poster_path") else series_data.get("poster")
            series_data["backdrop"] = f"{self.image_base}{tmdb['backdrop_path']}" if tmdb.get("backdrop_path") else ""
        return series_data

    def enrich_episode(self, episode_data: dict, tmdb_id: int):
        """Add TMDB still image to episode data."""
        if not tmdb_id:
            return episode_data
        try:
            details = self.get_episode_details(tmdb_id, episode_data["season"], episode_data["episode"])
            if details and details.get("still_path"):
                episode_data["still"] = f"{self.image_base}{details['still_path']}"
            # Also update title if TMDB has a better one
            if details and details.get("name") and len(details["name"]) > 5:
                episode_data["title"] = details["name"]
        except Exception as e:
            print(f"⚠️ TMDB enrich failed for ep {episode_data['episode']}: {e}")
        return episode_data
