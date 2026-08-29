"""Route schema stub (M6 placeholder)."""
from pydantic import BaseModel
from typing import List, Dict, Any

class RouteOption(BaseModel):
    route_id: str
    distance_km: float
    duration: str
    risk_score: float
    geofence_violations: List[str]
    hazards: List[str]

class RouteResponse(BaseModel):
    routes: List[RouteOption]
