import time
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

class Geocoder:
    def __init__(self, user_agent: str = "unsplash_places_project_raphael"):
        self.geolocator = Nominatim(user_agent=user_agent)

    def geocode(self, location_name: str) -> tuple[float, float] | None:
        """Geocode a location name to (lat, lon)."""
        try:
            # Rate limiting
            time.sleep(1)
            location = self.geolocator.geocode(location_name)
            if location:
                return location.latitude, location.longitude
        except (GeocoderTimedOut, GeocoderServiceError) as e:
             print(f"  -> Geocoding error for {location_name}: {e}")
        return None
