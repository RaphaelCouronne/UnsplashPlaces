import polars as pl
from unsplash_places.config import _ROOT_PATH
from unsplash_places.fetcher import fetch_url
from unsplash_places.scraper import extract_location
from unsplash_places.geocoding import Geocoder
from unsplash_places.visualization import create_map

from unsplash_places.database import Database

def main(retry_failed_geocoding=False):
    # 1. Load CSV
    csv_path = _ROOT_PATH / 'data/unsplash_places.csv'
    if not csv_path.exists():
        print(f"Error: CSV file not found at {csv_path}")
        return

    df = pl.read_csv(csv_path)
    df = df.select(["Title", "Url", "Publication Year"]).unique()
    
    print(f"Processing {len(df)} items...")

    # 2. Setup Geocoder and Database
    geocoder = Geocoder()
    db = Database()
    locations_data = []

    # 3. Iterate, Scrape, Geocode
    for row in df.iter_rows(named=True):
        url = row['Url']
        html_content = fetch_url(url)
        
        if not html_content:
            continue
            
        loc_data = extract_location(html_content)
        if not loc_data:
            continue
            
        loc_name = loc_data["name"]
        image_url = loc_data["image_url"]

        # Check DB for existing or failed location
        cached_loc = db.get_location(loc_name)
        if cached_loc:
            # cached_loc is (lat, lon, image_url)
            lat, lon, cached_img = cached_loc
            # Update image_url if not present in cache but present now?
            # For now, just use what we have or prefer the new one if cache is null?
            # Let's keep simple: use cached.
            # If cached_img is None and we have image_url, maybe update?
            if not cached_img and image_url:
                db.save_location(loc_name, lat, lon, image_url)
                cached_img = image_url

            locations_data.append({
                "Title": row['Title'],
                "Url": row['Url'],
                "Location": loc_name,
                "Latitude": lat,
                "Longitude": lon,
                "Image": cached_img
            })
            continue

        if not retry_failed_geocoding:
            if db.is_failed_location(loc_name):
                continue
            
        print(f"Geocoding new location: {loc_name}")
        
        # Geocode
        coords = geocoder.geocode(loc_name)
        if coords:
            lat, lon = coords
            print(f"  -> Coords: {lat}, {lon}")
            db.save_location(loc_name, lat, lon, image_url)
            locations_data.append({
                "Title": row['Title'],
                "Url": row['Url'],
                "Location": loc_name,
                "Latitude": lat,
                "Longitude": lon,
                "Image": image_url
            })
        else:
            print(f"  -> Could not geocode: {loc_name}")
            db.mark_failed_location(loc_name)

    # 4. Create Map
    create_map(locations_data)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument( '-r', "--retry-failed-geocoding", action="store_true")
    args = parser.parse_args()

    retry_failed_geocoding = args.retry_failed_geocoding    
    main(retry_failed_geocoding=retry_failed_geocoding)
