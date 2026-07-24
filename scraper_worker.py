import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.scraper.crawler import Crawler

if __name__ == "__main__":
    print("🔄 Starting Animesalt 24x7 Crawler...")
    crawler = Crawler()
    # Run every 6 hours (adjust as needed)
    crawler.run_forever(interval_seconds=21600)
