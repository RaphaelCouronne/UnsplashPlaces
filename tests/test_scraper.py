from pathlib import Path
from unsplash_places.scraper import extract_location

def test_scrape_sample_1():
    file_path = Path("data/sample_page_1.htm")
    content = file_path.read_text(encoding="utf-8")
    data = extract_location(content)
    
    assert data is not None
    assert data["name"] == "Hisma Desert – NEOM, Saudi Arabia"
    # Check that image_url starts with expected unsplash domain and contains photo ID
    assert "https://images.unsplash.com/photo-" in data["image_url"]
    assert "1682685796186" in data["image_url"]

def test_scrape_sample_2():
     file_path = Path("data/sample_page_2.htm")
     content = file_path.read_text(encoding="utf-8")
     data = extract_location(content)
     
     assert data is not None
     assert isinstance(data["name"], str)
     assert len(data["name"]) > 0
     
     if data["image_url"]:
         assert "https://images.unsplash.com/" in data["image_url"]
