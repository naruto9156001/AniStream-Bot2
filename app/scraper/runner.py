from app.scraper.client import AnimeSaltClient
from app.scraper.parser import parse_series_list, parse_series_details, parse_episodes
from app.database import series, episodes
import logging
import time

logger = logging.getLogger(__name__)
client = AnimeSaltClient()

def run_full_scrape():
    logger.info("🚀 Starting Full Scrape...")

    # Homepage scrape
    soup = client.get(client.base_url)
    if not soup:
        return

    anime_list = parse_series_list(soup)
    logger.info(f"Found {len(anime_list)} anime")

    for anime in anime_list[:30]:  # Limit for first run
        slug = anime['slug']
        
        # Check if already exists
        if series.find_one({"slug": slug}):
            logger.info(f"Skipping {slug} - already exists")
            continue

        # Get full details
        detail_soup = client.get(anime['url'])
        if detail_soup:
            details = parse_series_details(detail_soup, slug)
            series.insert_one(details)
            logger.info(f"Saved series: {details['title']}")

        time.sleep(2)

    logger.info("✅ Scrape completed!")