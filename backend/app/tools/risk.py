"""Risk tool - deterministic scoring per docs 15_ML_ANALYTICS, 02 SAFE."""
from typing import Dict, Any

def calculate_risk(wind_speed: float = 0, wave_height: float = 0, rainfall: float = 0, inside_geofence: bool = False) -> Dict[str, Any]:
    """Rule-based deterministic, LLM only explains."""
    score = 0
    factors = []
    if wind_speed > 15:
        score += 40
        factors.append(f"High wind {wind_speed} m/s")
    elif wind_speed > 10:
        score += 20
        factors.append(f"Moderate wind {wind_speed} m/s")
    if wave_height > 2.5:
        score += 30
        factors.append(f"High waves {wave_height} m")
    elif wave_height > 1.5:
        score += 15
        factors.append(f"Moderate waves {wave_height} m")
    if rainfall > 5:
        score += 20
        factors.append(f"Heavy rainfall {rainfall} mm")
    if inside_geofence:
        score += 25
        factors.append("Inside restricted/protected zone")
    if score >= 70:
        level = "HIGH"
    elif score >= 40:
        level = "MODERATE"
    elif score >= 20:
        level = "LOW"
    else:
        level = "LOW"
        factors.append("Conditions favorable")
    return {"risk_score": score, "risk_level": level, "risk_factors": factors, "inputs": {"wind_speed": wind_speed, "wave_height": wave_height}}
