from bs4 import BeautifulSoup
from pathlib import Path

def extract_location(html_content: str) -> str | None:
    soup = BeautifulSoup(html_content, "html.parser")
    # Look for the map marker icon
    # Based on grep: <svg class="detailIcon..." ...><desc>A map marker</desc></svg>
    # The sibling span contains the text.
    
    # Method: Find svg with desc "A map marker"
    markers = soup.find_all("desc", string="A map marker")
    for marker in markers:
        # parent is svg. parent's next sibling is the span with text.
        svg = marker.parent
        if svg:
             location_span = svg.find_next_sibling("span")
             if location_span:
                 return " ".join(location_span.get_text(strip=True).split())
    return None

def parse_file(file_path: Path) -> str | None:
    with open(file_path, "r", encoding="utf-8") as f:
        return extract_location(f.read())


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
