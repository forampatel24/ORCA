"""Risk Engine - docs 15_ML_ANALYTICS 26-30 deterministic 4 levels."""
from typing import Dict, Any, List

# Config-driven thresholds per docs 81
THRESHOLDS = {
    "wind": {"moderate": 10, "high": 15, "very_high": 20},
    "wave": {"moderate": 1.5, "high": 2.5, "very_high": 3.5},
    "rainfall": {"moderate": 5, "high": 15},
}

def calculate_risk(
    wind_speed: float = 0,
    wave_height: float = 0,
    wave_period: float = 0,
    rainfall: float = 0,
    lightning: bool = False,
    cyclone: bool = False,
    inside_geofence: bool = False,
    visibility: float = 10,
) -> Dict[str, Any]:
    score = 0
    factors: List[str] = []
    # wind
    if wind_speed >= THRESHOLDS["wind"]["very_high"]:
        score += 50; factors.append(f"Very high wind {wind_speed} m/s")
    elif wind_speed >= THRESHOLDS["wind"]["high"]:
        score += 35; factors.append(f"High wind {wind_speed} m/s")
    elif wind_speed >= THRESHOLDS["wind"]["moderate"]:
        score += 15; factors.append(f"Moderate wind {wind_speed} m/s")
    # wave
    if wave_height >= THRESHOLDS["wave"]["very_high"]:
        score += 40; factors.append(f"Very high waves {wave_height} m")
    elif wave_height >= THRESHOLDS["wave"]["high"]:
        score += 30; factors.append(f"High waves {wave_height} m")
    elif wave_height >= THRESHOLDS["wave"]["moderate"]:
        score += 10; factors.append(f"Moderate waves {wave_height} m")
    # rainfall
    if rainfall >= THRESHOLDS["rainfall"]["high"]:
        score += 20; factors.append(f"Heavy rainfall {rainfall} mm")
    elif rainfall >= THRESHOLDS["rainfall"]["moderate"]:
        score += 10; factors.append(f"Moderate rainfall {rainfall} mm")
    # lightning/cyclone
    if lightning:
        score += 25; factors.append("Lightning activity")
    if cyclone:
        score += 50; factors.append("Cyclone warning active")
    # geofence
    if inside_geofence:
        score += 30; factors.append("Inside restricted/protected zone")
    # visibility
    if visibility < 2:
        score += 20; factors.append(f"Low visibility {visibility} km")
    # levels per docs 27
    if score >= 80:
        level = "VERY_HIGH"
    elif score >= 60:
        level = "HIGH"
    elif score >= 30:
        level = "MODERATE"
    else:
        level = "LOW"
        if not factors: factors.append("Conditions favorable")
    return {
        "risk_score": score,
        "risk_level": level,
        "risk_factors": factors,
        "confidence": "HIGH" if not lightning and not cyclone else "MEDIUM",
        "inputs": {"wind_speed": wind_speed, "wave_height": wave_height, "rainfall": rainfall, "lightning": lightning, "cyclone": cyclone},
        "thresholds": THRESHOLDS,
    }

# Safety override per docs 25
def safety_override(pfz_suitability: str, risk_level: str) -> str:
    if risk_level in ("VERY_HIGH", "HIGH") and pfz_suitability == "HIGH":
        return "AVOID - Safety overrides suitability"
    return "OK"
