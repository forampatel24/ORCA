"""Routing engine - docs 15 42-48 multi-objective."""
from typing import Dict, Any, List
import math

# Config-driven weights per docs 81 routing_weights.yaml
WEIGHTS = {"distance": 0.3, "time": 0.2, "risk": 0.5}

def haversine(lat1, lon1, lat2, lon2) -> float:
    R=6371
    dlat=math.radians(lat2-lat1); dlon=math.radians(lon2-lon1)
    a=math.sin(dlat/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlon/2)**2
    return 2*R*math.asin(math.sqrt(a))

def score_route(origin: Dict[str,float], destination: Dict[str,float], risk_score: int, geofence_penalty: int = 0) -> Dict[str, Any]:
    dist = haversine(origin["lat"], origin["lon"], destination["lat"], destination["lon"])
    time_h = dist / 20  # 20 km/h vessel avg
    # Normalize risk 0-100 -> 0-1
    risk_norm = risk_score/100
    dist_norm = min(dist/100, 1.0)
    time_norm = min(time_h/10, 1.0)
    cost = WEIGHTS["distance"]*dist_norm + WEIGHTS["time"]*time_norm + WEIGHTS["risk"]*risk_norm + geofence_penalty
    return {
        "distance_km": round(dist,2),
        "time_h": round(time_h,2),
        "risk_score": risk_score,
        "geofence_penalty": geofence_penalty,
        "cost": round(cost,3),
        "weights": WEIGHTS,
        "origin": origin, "destination": destination,
        "status": "rejected" if geofence_penalty > 10 else "optimized"
    }

def find_safe_route(origin, destination, hazards: List[Dict], geofences: List[Dict]) -> Dict[str, Any]:
    # Simplified A* placeholder - M6 uses direct + penalty per docs 44 geofence penalty
    penalty = 100 if any(g.get("inside_geofence") for g in geofences) else 0
    # hazard risk from max wind/wave
    max_risk = max([h.get("risk_score", 0) for h in hazards], default=30)
    return score_route(origin, destination, max_risk, penalty)
