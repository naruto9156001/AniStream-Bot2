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

    # Homepage se series list
    soup = client.get(client.base_url)
    if not soup:
        logger.error("Failed to fetch homepage")
        return

    anime_list = parse_series_list(soup)
    logger.info(f"Found {len(anime_list)} anime on homepage")

    saved_series = 0
    saved_episodes = 0

    for anime in anime_list[:40]:   # Adjust limit as needed
        slug = anime['slug']

        # Agar already exist karta hai toh skip
        if series.find_one({"slug": slug}):
            logger.info(f"⏭️ Skipping {slug} - already exists")
            continue

        # Series details page
        detail_soup = client.get(anime['url'])
        if not detail_soup:
            continue

        # Save series
        details = parse_series_details(detail_soup, slug)
        series.insert_one(details)
        saved_series += 1
        logger.info(f"✅ Saved Series: {details['title']}")

        # Save episodes
        episode_list = parse_episodes(detail_soup, slug)
        if episode_list:
            episodes.insert_many(episode_list)
            saved_episodes += len(episode_list)
            logger.info(f"   → Saved {len(episode_list)} episodes")

        time.sleep(3)  # Be gentle on server

    logger.info(f"🎉 Scrape Completed! Series: {saved_series} | Episodes: {saved_episodes} | Time: {datetime.utcnow() - start_time}")
