import requests
import time
from unsplash_places.database import Database

# We maintain a single DB instance or check if we should create one here.
# For simplicity, let's instantiate it here.
db = Database()

def fetch_url(url: str) -> str | None:
    """Fetch URL with database caching."""
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
