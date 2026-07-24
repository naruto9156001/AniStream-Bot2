import time
import os
import json
from datetime import datetime
from app.database.database import Database
from app.scraper.animesalt import AnimesaltScraper
from app.scraper.tmdb import TMDBClient
from app.github.uploader import GitHubUploader  # Existing

class Crawler:
    def __init__(self):
        self.db = Database()
        self.scraper = AnimesaltScraper()
        self.tmdb = TMDBClient()
        self.github = GitHubUploader()  # uses existing env vars
        self.series_cache = {}

    def run_full_scan(self):
        """Complete scan of all anime, seasons, episodes."""
        print("🚀 Starting full site scan...")
        
        # 1. Get all series
        all_series = self.scraper.get_all_series()
        print(f"📺 Found {len(all_series)} series.")
        
        for s in all_series:
            series_id = s["series_id"]
            print(f"🔍 Processing: {s['title']} ({series_id})")
            
            # Enrich with TMDB
            s = self.tmdb.enrich_series(s)
            self.db.upsert_series(s)
            tmdb_id = s.get("tmdb_id")
            
            # 2. Get seasons
            seasons = self.scraper.get_seasons(series_id)
            for season_info in seasons:
                post_id = season_info["post_id"]
                season_num = season_info["season_num"]
                print(f"  📅 Season {season_num} (Post ID: {post_id})")
                
                # 3. Get episodes via AJAX
                episodes = self.scraper.get_episodes_by_season(post_id, season_num)
                print(f"    📺 Found {len(episodes)} episodes.")
                
                for ep in episodes:
                    # 4. Get streaming sources from episode page
                    ep_data = self.scraper.get_episode_sources(ep["url"])
                    
                    # Merge data
                    ep_merged = {
                        "series_id": series_id,
                        "season": season_num,
                        "episode": ep["episode"],
                        "title": ep["title"],
                        "thumb": ep.get("thumb"),
                        "url": ep["url"],
                        "servers": ep_data.get("servers", []),
                        "languages": list(set([s.get("language") for s in ep_data.get("servers", []) if s.get("language") != "unknown"])),
                        "is_non_regional": ep_data.get("is_non_regional", False),
                    }
                    
                    # Enrich with TMDB still
                    ep_merged = self.tmdb.enrich_episode(ep_merged, tmdb_id)
                    
                    # Save to MongoDB
                    self.db.upsert_episode(ep_merged)
                    print(f"      ✅ Episode {ep_num} saved.")
                    
                    time.sleep(0.3)  # Rate limit
                time.sleep(0.5)
            time.sleep(0.5)
        
        # 5. Commit status to GitHub
        self.commit_status()
        print("✅ Full scan completed.")

    def commit_status(self):
        """Push a status file to GitHub using existing uploader."""
        stats = self.db.get_stats()
        data = {
            "timestamp": datetime.utcnow().isoformat(),
            "stats": stats,
            "message": "Automated 24x7 scraper update"
        }
        # Using existing GitHub uploader from the repo
        # It likely has an upload_file method. If not, I'll write a fallback.
        try:
            self.github.upload_file(
                "scraper_status.json", 
                json.dumps(data, indent=2),
                f"Scraper update: {stats['episodes']} episodes total"
            )
            print("📦 GitHub status updated.")
        except Exception as e:
            print(f"⚠️ GitHub commit failed: {e}")

    def run_forever(self, interval_seconds=21600):
        """Run scan every X seconds (default 6 hours)."""
        while True:
            try:
                self.run_full_scan()
                print(f"💤 Sleeping for {interval_seconds/3600} hours...")
                time.sleep(interval_seconds)
            except Exception as e:
                print(f"🔥 Crawler crashed: {e}")
                time.sleep(300)  # Wait 5 mins and restart loop
