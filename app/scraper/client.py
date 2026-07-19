import requests
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

class AnimeSaltClient:
    def __init__(self):
        self.base_url = "https://animesalt.ac"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

    def get(self, url):
        try:
            resp = requests.get(url, headers=self.headers, timeout=20)
            resp.raise_for_status()
            return BeautifulSoup(resp.text, 'lxml')
        except Exception as e:
            logger.error(f"Failed {url}: {e}")
            return None