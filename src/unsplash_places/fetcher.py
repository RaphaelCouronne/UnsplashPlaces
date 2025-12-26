import requests
import time
import hashlib
from pathlib import Path
from unsplash_places.config import _ROOT_PATH

CACHE_DIR = _ROOT_PATH / 'data/cache'
CACHE_DIR.mkdir(parents=True, exist_ok=True)

def fetch_url(url: str) -> str | None:
    """Fetch URL with caching."""
    url_hash = hashlib.md5(url.encode()).hexdigest()
    cache_file = CACHE_DIR / f"{url_hash}.html"
    
    if cache_file.exists():
        return cache_file.read_text(encoding="utf-8")
    
    try:
        print(f"Fetching {url}...")
        # Use a real user agent to be polite and avoid blocking
        headers = {"User-Agent": "UnsplashPlacesBot/1.0"}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            cache_file.write_text(response.text, encoding="utf-8")
            time.sleep(1) # Polite delay
            return response.text
        else:
            print(f"Failed to fetch {url}: {response.status_code}")
    except Exception as e:
        print(f"Error fetching {url}: {e}")
    return None
