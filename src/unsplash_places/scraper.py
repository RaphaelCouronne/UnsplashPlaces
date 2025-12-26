from bs4 import BeautifulSoup
from pathlib import Path

def extract_location(html_content: str) -> dict | None:
    soup = BeautifulSoup(html_content, "html.parser")
    
    # 1. Get Location Name
    # Look for the map marker icon
    location_name = None
    markers = soup.find_all("desc", string="A map marker")
    for marker in markers:
        svg = marker.parent
        if svg:
             location_span = svg.find_next_sibling("span")
             if location_span:
                 location_name = " ".join(location_span.get_text(strip=True).split())
                 break
    
    if not location_name:
        return None

    # 2. Get Image URL
    image_url = None
    meta_image = soup.find("meta", property="og:image")
    if meta_image:
        image_url = meta_image.get("content")

    return {
        "name": location_name,
        "image_url": image_url
    }

def parse_file(file_path: Path) -> str | None:
    with open(file_path, "r", encoding="utf-8") as f:
        data = extract_location(f.read())
        return data["name"] if data else None


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
