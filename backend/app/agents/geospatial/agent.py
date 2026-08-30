"""Geospatial Agent - docs 06 AI-014 - deterministic PostGIS."""
from app.tools.geospatial import check_geofence, calculate_distance

class GeospatialAgent:
    name = "geospatial_agent"
    tools = ["check_geofence", "calculate_distance"]
    async def run(self, lat: float = 19.0, lon: float = 72.8) -> dict:
        return check_geofence(lat, lon)

geospatial_agent = GeospatialAgent()
