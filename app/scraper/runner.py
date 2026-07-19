from app.scraper.client import AnimeSaltClient
from app.scraper.parser import parse_series_list, parse_series_details, parse_episodes
from app.database import series, episodes
import logging
import time
from datetime import datetime

logger = logging.getLogger(__name__)
client = AnimeSaltClient()

def run_full_scrape():
    logger.info("🚀 Starting Full AnimeSalt Scrape...")
    start_time = datetime.utcnow()

    page = 1
    total_saved = 0

    while True:
        logger.info(f"Scraping page {page}...")
        soup = client.get(f"{client.base_url}/?page={page}")
        
        if not soup:
            break

        anime_list = parse_series_list(soup)
        if not anime_list:
            logger.info("No more anime found.")
            break

        logger.info(f"Page {page}: Found {len(anime_list)} anime")

        for anime in anime_list:
            slug = anime['slug']

            if series.find_one({"slug": slug}):
                continue

            detail_soup = client.get(anime['url'])
            if not detail_soup:
                continue

            details = parse_series_details(detail_soup, slug)
            series.insert_one(details)
            total_saved += 1
            logger.info(f"✅ Saved: {details['title']}")

            episode_list = parse_episodes(detail_soup, slug)
            if episode_list:
                episodes.insert_many(episode_list)
                logger.info(f"   → {len(episode_list)} episodes")

            time.sleep(3)

        page += 1
        time.sleep(5)

    logger.info(f"🎉 Full Crawl Completed! Total Series: {total_saved}")
    logger.info(f"Time Taken: {datetime.utcnow() - start_time}")

if __name__ == "__main__":
    run_full_scrape()
