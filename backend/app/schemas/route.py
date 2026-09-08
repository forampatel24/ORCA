"""Route schema stub (M6 placeholder)."""
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class RouteOption(BaseModel):
    route_id: str
    distance_km: float
    duration: str
    risk_score: float
    geofence_violations: List[str]
    hazards: List[str]
    coordinates: Optional[List[List[float]]] = None  # [[lon,lat],...] safe polyline
    instructions: Optional[List[str]] = None  # turn-by-turn e.g. "Head SW 232° for 12.3 km"
    pfz_start: Optional[str] = None
    pfz_end: Optional[str] = None

class RouteResponse(BaseModel):
    routes: List[RouteOption]
