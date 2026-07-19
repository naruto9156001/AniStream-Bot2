def parse_series_list(soup):
    items = []
    for post in soup.select('li.post, article.post'):
        link = post.select_one('a[href*="/series/"]')
        if not link:
            continue
        href = link.get('href', '')
        title_tag = post.select_one('h2.entry-title')
        title = title_tag.text.strip() if title_tag else ''

        if title and href:
            slug = href.strip('/').split('/')[-1]
            img = post.select_one('img')
            poster = img.get('data-src') or img.get('src', '') if img else ''

            items.append({
                "title": title,
                "slug": slug,
                "url": f"https://animesalt.ac{href}" if not href.startswith('http') else href,
                "poster": poster,
                "source": "animesalt.ac"
            })
    return items

def parse_series_details(soup, slug):
    title = soup.select_one('h1, .entry-title')
    title = title.text.strip() if title else slug.replace('-', ' ').title()

    desc = soup.select_one('.overview, .description, p')
    description = desc.text.strip() if desc else ''

    img = soup.select_one('img[src*="poster"], img[data-src*="poster"]')
    poster = img.get('data-src') or img.get('src', '') if img else ''

    return {
        "title": title,
        "slug": slug,
        "description": description,
        "poster": poster,
        "status": "Ongoing",
        "source": "animesalt.ac"
    }

def parse_episodes(soup, slug):
    episodes = []
    for item in soup.select('li.post.episodes, .episode-item'):
        num_tag = item.select_one('.num-epi, .episode-number')
        num = int(''.join(filter(str.isdigit, num_tag.text))) if num_tag else None

        title_tag = item.select_one('h2, .episode-title, a')
        title = title_tag.text.strip() if title_tag else f"Episode {num}"

        if num:
            episodes.append({
                "anime_slug": slug,
                "episode": num,
                "title": title,
                "episode_id": f"{slug}-ep{num}",
                "language": "hindi",
                "quality": "720p",
                "status": "available"
            })
    return episodes