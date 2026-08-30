"""Unit tests - Risk engine per docs 17_TESTING TEST-006."""
from app.analytics.risk.engine import calculate_risk

def test_risk_low():
    r = calculate_risk(wind_speed=5, wave_height=0.5)
    assert r["risk_level"] == "LOW"

def test_risk_moderate():
    r = calculate_risk(wind_speed=12, wave_height=1.8)
    assert r["risk_level"] in ("LOW","MODERATE")

def test_risk_high():
    r = calculate_risk(wind_speed=16, wave_height=2.8, inside_geofence=True)
    assert r["risk_level"] in ("HIGH","VERY_HIGH")

def test_risk_very_high_cyclone():
    r = calculate_risk(wind_speed=22, wave_height=4.0, lightning=True, cyclone=True)
    assert r["risk_level"] == "VERY_HIGH"
    assert r["risk_score"] > 80

def test_risk_safety_override():
    from app.analytics.risk.engine import safety_override
    assert safety_override("HIGH","VERY_HIGH") == "AVOID - Safety overrides suitability"
