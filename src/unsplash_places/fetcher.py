import asyncio
import aiohttp
import requests
import time
from unsplash_places.database import Database

# We maintain a single DB instance or check if we should create one here.
# For simplicity, let's instantiate it here.
db = Database()

async def fetch_url_async(session: aiohttp.ClientSession, url: str) -> str | None:
    """Fetch a single URL asynchronously."""
    # Check cache first (sync DB access is okay for now, or could make it thread-based if blocking)
    # For a few hundred items, sync DB check is negligible compared to network.
    cached_content = db.get_page(url)
    if cached_content:
        return cached_content

    try:
        print(f"Fetching {url}...")
        headers = {"User-Agent": "UnsplashPlacesBot/1.0"}
        async with session.get(url, headers=headers, timeout=10) as response:
            if response.status == 200:
                content = await response.text()
                db.save_page(url, content)
                return content
            else:
                print(f"Failed to fetch {url}: {response.status}")
    except Exception as e:
        print(f"Error fetching {url}: {e}")
    return None

async def fetch_all(urls: list[str]) -> dict[str, str | None]:
    """Fetch multiple URLs concurrently with rate limiting."""
    results = {}
    timeout = aiohttp.ClientTimeout(total=60)
    conn = aiohttp.TCPConnector(limit=5) # Limit concurrency to be polite
    
    async with aiohttp.ClientSession(connector=conn, timeout=timeout) as session:
        tasks = []
        for url in urls:
            tasks.append(fetch_url_async(session, url))
        
        # Gather results
        pages = await asyncio.gather(*tasks)
        
        for url, content in zip(urls, pages):
            results[url] = content
            
    return results

def fetch_url(url: str) -> str | None:
    """Legacy sync fetch URL with database caching."""
    cached_content = db.get_page(url)
    if cached_content:
        return cached_content
    
    try:
        print(f"Fetching {url}...")
        headers = {"User-Agent": "UnsplashPlacesBot/1.0"}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            db.save_page(url, response.text)
            time.sleep(1) # Polite delay
            return response.text
        else:
            print(f"Failed to fetch {url}: {response.status_code}")
    except Exception as e:
        print(f"Error fetching {url}: {e}")
    return None
