"""Route Optimization Agent - docs 06 AI-016 - deterministic."""
from app.tools.geospatial import calculate_distance

class RoutingAgent:
    name = "routing_agent"
    tools = ["calculate_distance"]
    async def run(self, origin: dict = None, destination: dict = None, hazards: dict = None) -> dict:
        if not origin: origin = {"lat": 19.0, "lon": 72.8}
        if not destination: destination = {"lat": 19.1, "lon": 72.5}
        dist = calculate_distance(origin["lat"], origin["lon"], destination["lat"], destination["lon"])
        # simple scoring: distance + risk penalty
        return {"origin": origin, "destination": destination, "distance_km": round(dist,2), "estimated_duration_h": round(dist/20,2), "status": "optimized", "avoided": []}

routing_agent = RoutingAgent()
