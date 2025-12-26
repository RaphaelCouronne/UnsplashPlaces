import pandas as pd
from unsplash_places.config import _ROOT_PATH
from unsplash_places.fetcher import fetch_url
from unsplash_places.scraper import extract_location
from unsplash_places.geocoding import Geocoder
from unsplash_places.visualization import create_map

def main():
    # 1. Load CSV
    csv_path = _ROOT_PATH / 'data/unsplash_places.csv'
    if not csv_path.exists():
        print(f"Error: CSV file not found at {csv_path}")
        return

    df = pd.read_csv(csv_path)
    df = df[["Title", "Url", "Publication Year"]].drop_duplicates()
    
    print(f"Processing {len(df)} items...")

    # 2. Setup Geocoder
    geocoder = Geocoder()
    locations_data = []

    # 3. Iterate, Scrape, Geocode
    for index, row in df.iterrows():
        url = row['Url']
        html_content = fetch_url(url)
        
        if not html_content:
            continue
            
        loc_name = extract_location(html_content)
        if not loc_name:
            continue
            
        print(f"Found location: {loc_name}")
        
        # Geocode
        coords = geocoder.geocode(loc_name)
        if coords:
            lat, lon = coords
            print(f"  -> Coords: {lat}, {lon}")
            locations_data.append({
                "Title": row['Title'],
                "Url": row['Url'],
                "Location": loc_name,
                "Latitude": lat,
                "Longitude": lon
            })
        else:
            print(f"  -> Could not geocode: {loc_name}")

    # 4. Create Map
    create_map(locations_data)

if __name__ == "__main__":
    main()
