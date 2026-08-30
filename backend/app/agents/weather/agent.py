"""Weather & Hazard Agent - docs 06 AI-012."""
from app.tools.weather import get_weather, get_hazards

class WeatherAgent:
    name = "weather_agent"
    tools = ["get_weather", "get_hazards"]
    async def run(self, lat: float = 19.0, lon: float = 72.8) -> dict:
        w = get_weather(lat, lon)
        h = get_hazards(lat, lon)
        return {"weather": w, "hazards": h}

weather_agent = WeatherAgent()
