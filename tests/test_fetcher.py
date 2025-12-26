import polars as pl
from unsplash_places.config import _ROOT_PATH
from unsplash_places.fetcher import fetch_url
import pytest

def test_fetch_first_two_urls():
    # Load the dataframe to get real URLs
    csv_path = _ROOT_PATH / 'tests/data/unsplash_places.csv'
    if not csv_path.exists():
        pytest.skip("CSV file not found")
        
    df = pl.read_csv(csv_path)
    # Get first 2 URLs
    urls = df['Url'].head(2).to_list()
    
    for url in urls:
        print(f"Testing fetch for: {url}")
        content = fetch_url(url)
        assert content is not None
        assert len(content) > 0
        assert "<html" in content.lower() or "<!doctype html" in content.lower()
