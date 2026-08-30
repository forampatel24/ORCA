"""Risk Assessment Agent - docs 06 AI-015 + 15_ML 26-30 deterministic 4 levels."""
from app.analytics.risk.engine import calculate_risk, safety_override

class RiskAgent:
    name = "risk_agent"
    tools = ["calculate_risk"]
    async def run(self, weather: dict = None, ocean: dict = None, geofence: dict = None) -> dict:
        w = weather.get("weather", weather) if weather and isinstance(weather, dict) else {}
        if "weather" in w: w = w["weather"]
        o = ocean.get("ocean", ocean) if ocean and isinstance(ocean, dict) else {}
        if "ocean" in o: o = o["ocean"]
        g = geofence or {}
        wind = w.get("wind_speed", 12.5)
        wave = o.get("wave_height", 1.2) if isinstance(o, dict) else 1.2
        rain = w.get("rainfall", 0)
        inside = bool(g.get("inside_geofence") or g.get("inside_protected"))
        # Use enhanced engine
        result = calculate_risk(wind_speed=wind, wave_height=wave, rainfall=rain, inside_geofence=inside)
        # Add safety override concept per docs 25
        result["safety_override"] = safety_override("HIGH", result["risk_level"])
        return result

risk_agent = RiskAgent()
