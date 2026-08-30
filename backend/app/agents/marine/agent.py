"""Marine Data Agent - docs 06_AGENT_SPEC AI-011."""
from typing import Dict, Any
from app.tools.pfz import get_nearest_pfz, get_pfz_all
from app.tools.ocean import get_ocean

class MarineAgent:
    name = "marine_agent"
    tools = ["get_nearest_pfz", "get_ocean"]

    async def run(self, lat: float = 19.0, lon: float = 72.8, radius_km: float = 50) -> Dict[str, Any]:
        pfz = get_nearest_pfz(lat, lon, radius_km)
        ocean = get_ocean(lat, lon)
        return {"pfz": pfz, "ocean": ocean, "count": len(pfz), "source": "pfz_observations + ocean_observations"}

marine_agent = MarineAgent()
