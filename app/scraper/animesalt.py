import requests
from bs4 import BeautifulSoup
import re
import time
from typing import List, Dict, Optional

class AnimesaltScraper:
    def __init__(self):
        self.base = "https://animesalt.link"
        self.ajax_url = f"{self.base}/wp-admin/admin-ajax.php"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    # ---------- GET ALL SERIES FROM SITEMAP / PAGINATION ----------
    def get_all_series(self) -> List[Dict]:
        """Fetch all series from the site (pagination)."""
        series_list = []
        page = 1
        while True:
            url = f"{self.base}/series/page/{page}/"
            resp = self.session.get(url)
            if resp.status_code != 200:
                break
            soup = BeautifulSoup(resp.text, 'html.parser')
            articles = soup.find_all('article', class_='movies')
            if not articles:
                break
            
            for art in articles:
                link = art.find('a', class_='lnk-blk')
                if not link:
                    continue
                href = link.get('href')
                slug = href.strip('/').split('/')[-1]
                title_elem = art.find('h2', class_='entry-title')
                title = title_elem.text.strip() if title_elem else slug
                
                img = art.find('img')
                img_src = img.get('data-src') or img.get('src') if img else ''
                
                series_list.append({
                    "series_id": slug,
                    "title": title,
                    "url": href,
                    "poster": img_src
                })
            print(f"✅ Fetched page {page}, total series: {len(series_list)}")
            page += 1
            time.sleep(0.5)  # Be gentle
        return series_list

    # ---------- FETCH SEASONS & EPISODES VIA AJAX ----------
    def get_seasons(self, series_id: str) -> List[Dict]:
        """Fetch seasons and episode ranges from the series detail page."""
        url = f"{self.base}/series/{series_id}/"
        resp = self.session.get(url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        seasons = []
        # Season buttons have class 'season-btn sel-temp'
        for btn in soup.find_all('a', class_='season-btn'):
            data_post = btn.get('data-post')
            data_season = btn.get('data-season')
            if not data_post or not data_season:
                continue
            text = btn.text.strip()
            # Extract range like "1-32 (32)"
            match = re.search(r'(\d+)-(\d+)', text)
            start_ep = int(match.group(1)) if match else None
            end_ep = int(match.group(2)) if match else None
            
            seasons.append({
                "post_id": data_post,
                "season_num": int(data_season),
                "label": text,
                "episode_range": [start_ep, end_ep],
                "non_regional": 'non-regional' in btn.get('class', [])
            })
        return seasons

    def get_episodes_by_season(self, post_id: str, season_num: int) -> List[Dict]:
        """Call AJAX endpoint to get episodes list for a specific season."""
        params = {
            'action': 'action_select_season',
            'season': season_num,
            'post': post_id
        }
        resp = self.session.get(self.ajax_url, params=params)
        if resp.status_code != 200:
            return []
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        episodes = []
        for li in soup.find_all('li'):
            article = li.find('article', class_='episodes')
            if not article:
                continue
            
            # Episode number
            num_span = article.find('span', class_='num-epi')
            ep_num = int(num_span.text.strip()) if num_span else None
            if not ep_num:
                continue
            
            # Title
            title_h2 = article.find('h2', class_='entry-title')
            title = title_h2.text.strip() if title_h2 else f"Episode {ep_num}"
            
            # URL
            link = article.find('a', class_='lnk-blk')
            ep_url = link.get('href') if link else ''
            if ep_url and not ep_url.startswith('http'):
                ep_url = self.base + ep_url
            
            # Thumbnail
            img = article.find('img')
            thumb = img.get('data-src') or img.get('src') if img else ''
            
            episodes.append({
                "episode": ep_num,
                "title": title,
                "url": ep_url,
                "thumb": thumb
            })
        return episodes

    # ---------- FETCH EPISODE STREAMING SOURCES ----------
    def get_episode_sources(self, episode_url: str) -> Dict:
        """Parse the episode page to extract iframe servers and languages."""
        resp = self.session.get(episode_url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Basic info
        title_h1 = soup.find('h1')
        title = title_h1.text.strip() if title_h1 else 'Unknown'
        
        info_div = soup.find('div', style=lambda x: x and 'color: var(--dim-text)' in x)
        season = episode = None
        ep_title = ""
        if info_div:
            text = info_div.text.strip()
            match = re.search(r'Season (\d+) Episode (\d+)\s*-\s*(.+)', text)
            if match:
                season = int(match.group(1))
                episode = int(match.group(2))
                ep_title = match.group(3).strip()
        
        # Find servers
        servers = []
        video_divs = soup.find_all('div', class_='video aa-tb')
        server_btns = soup.find_all('div', class_='server-btn')
        
        for idx, div in enumerate(video_divs):
            iframe = div.find('iframe')
            src = iframe.get('src') or iframe.get('data-src') if iframe else None
            if not src:
                continue
            
            # Try to get metadata from button
            name = f"SERVER {idx+1}"
            stype = ""
            if idx < len(server_btns):
                btn = server_btns[idx]
                name_elem = btn.find('div', class_='server-name')
                info_elem = btn.find('div', class_='server-info')
                if name_elem: name = name_elem.text.strip()
                if info_elem: stype = info_elem.text.strip()
            
            # Detect language from type or URL
            lang = "unknown"
            if stype.lower() in ['hindi', 'hin', 'playx']: lang = "hindi"
            elif stype.lower() in ['tamil', 'tam']: lang = "tamil"
            elif stype.lower() in ['telugu', 'tel']: lang = "telugu"
            elif stype.lower() in ['dub', 'dubbed']: lang = "english"
            elif stype.lower() in ['sub', 'subtitled']: lang = "japanese"
            
            # Also check if non-regional separator exists
            # If the URL itself has /sub or /dub
            if '/sub' in src: lang = "japanese"
            if '/dub' in src: lang = "english"
            
            servers.append({
                "name": name,
                "type": stype,
                "src": src,
                "language": lang
            })
        
        # If no servers found, try fallback (sometimes only iframe exists without button)
        if not servers:
            for div in video_divs:
                iframe = div.find('iframe')
                src = iframe.get('src') or iframe.get('data-src') if iframe else None
                if src:
                    servers.append({
                        "name": "SERVER 1",
                        "type": "default",
                        "src": src,
                        "language": "unknown"
                    })
        
        # Check if this is a non-regional episode (sub only)
        # Look for text "Below episodes aren't dubbed in regional languages"
        is_non_regional = "aren't dubbed" in soup.text
        
        return {
            "title": title,
            "season": season,
            "episode": episode,
            "episode_title": ep_title,
            "is_non_regional": is_non_regional,
            "servers": servers,
            "url": episode_url
        }
