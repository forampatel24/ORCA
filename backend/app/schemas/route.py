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
    pfz_start: Optional[str] = None
    pfz_end: Optional[str] = None

class RouteResponse(BaseModel):
    routes: List[RouteOption]
