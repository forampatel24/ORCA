"""Ocean Analytics Agent - docs 06 AI-013."""
from app.tools.ocean import get_ocean

class OceanAgent:
    name = "ocean_agent"
    tools = ["get_ocean"]
    async def run(self, lat: float = 19.0, lon: float = 72.8) -> dict:
        return {"ocean": get_ocean(lat, lon)}

ocean_agent = OceanAgent()
