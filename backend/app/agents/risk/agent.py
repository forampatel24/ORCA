"""Risk Assessment Agent - docs 06 AI-015 - deterministic."""
from app.tools.risk import calculate_risk

class RiskAgent:
    name = "risk_agent"
    tools = ["calculate_risk"]
    async def run(self, weather: dict = None, ocean: dict = None, geofence: dict = None) -> dict:
        w = weather.get("weather", weather) if weather else {}
        o = ocean.get("ocean", ocean) if ocean else {}
        g = geofence or {}
        wind = w.get("wind_speed", 12.5)
        wave = o.get("wave_height", 1.2) if isinstance(o, dict) else 1.2
        inside = bool(g.get("inside_geofence") or g.get("inside_protected"))
        return calculate_risk(wind_speed=wind, wave_height=wave, inside_geofence=inside)

risk_agent = RiskAgent()
