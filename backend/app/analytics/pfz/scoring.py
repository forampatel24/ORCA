"""PFZ Scoring - docs 15 19-25 weighted."""
from typing import Dict, Any

# Config-driven weights per docs 81 - pfz_weights.yaml concept
WEIGHTS = {"ocean": 0.3, "environment": 0.2, "safety": 0.35, "accessibility": 0.15}

def score_pfz(sst: float, chlorophyll: float, distance_km: float, safety_level: str) -> Dict[str, Any]:
    # ocean suitability: sst 27-29 ideal, chl 0.5-1.5 ideal
    ocean = 0
    if 27 <= sst <= 29: ocean += 50
    elif 26 <= sst <= 30: ocean += 30
    if 0.5 <= chlorophyll <= 1.5: ocean += 50
    elif 0.2 <= chlorophyll <= 2.0: ocean += 30
    ocean_score = min(ocean, 100) / 100
    # environment: distance penalty
    env = max(0, 100 - distance_km*2) / 100
    # safety: map risk level to score inverse
    safety_map = {"LOW": 1.0, "MODERATE": 0.6, "HIGH": 0.3, "VERY_HIGH": 0.0}
    safety = safety_map.get(safety_level, 0.5)
    # accessibility: closer is better
    access = max(0, 1 - distance_km/100)
    pfz_score = WEIGHTS["ocean"]*ocean_score + WEIGHTS["environment"]*env + WEIGHTS["safety"]*safety + WEIGHTS["accessibility"]*access
    safety_override = "AVOID" if safety_level in ("VERY_HIGH","HIGH") else "OK"
    return {
        "pfz_score": round(pfz_score, 3),
        "ocean_score": round(ocean_score,3),
        "env_score": round(env,3),
        "safety_score": round(safety,3),
        "access_score": round(access,3),
        "safety_override": safety_override,
        "weights": WEIGHTS,
        "inputs": {"sst": sst, "chlorophyll": chlorophyll, "distance_km": distance_km, "safety_level": safety_level},
    }
