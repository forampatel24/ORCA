"""PFZ scoring tests."""
from app.analytics.pfz.scoring import score_pfz

def test_pfz_high():
    s = score_pfz(28.2, 0.8, 15.2, "LOW")
    assert s["pfz_score"] > 0.7
    assert s["safety_override"] == "OK"

def test_pfz_safety_override():
    s = score_pfz(28.2, 0.8, 15.2, "VERY_HIGH")
    assert s["safety_override"] == "AVOID"
