import time
from geopy.geocoders import Nominatim, ArcGIS
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

class Geocoder:
    def __init__(self, user_agent: str = "unsplash_places_project_raphael"):
        self.nominatim = Nominatim(user_agent=user_agent)
        self.arcgis = ArcGIS(user_agent=user_agent)

    def geocode(self, location_name: str) -> tuple[float, float] | None:
        """Geocode a location name to (lat, lon)."""
        # Try Nominatim first
        try:
            time.sleep(1) # Rate limiting for Nominatim
            location = self.nominatim.geocode(location_name)
            if location:
                return location.latitude, location.longitude
        except (GeocoderTimedOut, GeocoderServiceError) as e:
             print(f"  -> Nominatim error for {location_name}: {e}")
        except Exception as e:
             print(f"  -> Nominatim unexpected error for {location_name}: {e}")

        # Fallback to ArcGIS
        try:
            print(f"  -> Falling back to ArcGIS for {location_name}...")
            location = self.arcgis.geocode(location_name)
            if location:
                return location.latitude, location.longitude
        except (GeocoderTimedOut, GeocoderServiceError) as e:
             print(f"  -> ArcGIS error for {location_name}: {e}")
        except Exception as e:
             print(f"  -> ArcGIS unexpected error for {location_name}: {e}")
             
        return None
