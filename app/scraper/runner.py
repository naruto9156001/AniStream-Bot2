from .animesalt import AnimesaltScraper

class ScraperRunner:
    def __init__(self):
        self.scraper = AnimesaltScraper()
    
    def get_episode(self, url: str):
        """Get episode details and streaming sources"""
        return self.scraper.get_episode_sources(url)
    
    def get_series_episodes(self, url: str, season: int = None):
        """Get all episodes of a series, optionally filtered by season"""
        series_id = url.strip('/').split('/')[-1]
        seasons = self.scraper.get_seasons(series_id)
        all_eps = []
        for s in seasons:
            if season is not None and s["season_num"] != season:
                continue
            eps = self.scraper.get_episodes_by_season(s["post_id"], s["season_num"])
            all_eps.extend(eps)
        return all_eps
    
    def search(self, query: str):
        """Search for anime"""
        return self.scraper.search_anime(query)
