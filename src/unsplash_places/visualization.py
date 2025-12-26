import folium
from pathlib import Path
from unsplash_places.config import _ROOT_PATH

def create_map(locations_data: list[dict], output_path: Path | None = None) -> Path | None:
    """Create a folium map from location data."""
    if not locations_data:
        print("No locations found to map.")
        return None

    # Center map on the first location or logical center
    center_lat = locations_data[0]['Latitude']
    center_lon = locations_data[0]['Longitude']
    m = folium.Map(location=[center_lat, center_lon], zoom_start=2)
    
    for item in locations_data:
        popup_html = f"<b>{item['Title']}</b><br>{item['Location']}"
        if item.get('Image'):
             popup_html += f"<br><img src='{item['Image']}' width='200' style='margin-top:5px;'>"
        popup_html += f"<br><a href='{item['Url']}' target='_blank'>More info</a>"

        folium.Marker(
            [item['Latitude'], item['Longitude']],
            popup=popup_html,
            tooltip=item['Location']
        ).add_to(m)
    
    if output_path is None:
        output_path = _ROOT_PATH / 'data/unsplash_map.html'
        
    m.save(output_path)
    print(f"Map saved to {output_path}")
    return output_path
