"""PFZ scoring tests - updated for Mumbai 15 Aug legit 0.139 chl."""
from app.analytics.pfz.scoring import score_pfz

def test_pfz_high():
    s = score_pfz(29.9, 0.139, 8, "LOW")
    assert s["pfz_score"] > 0.7
    assert s["safety_override"] == "OK"

def test_pfz_low_chl_still_ok():
    # Mumbai chl 0.139 is low but legit Copernicus, still scores via SST
    s = score_pfz(29.9, 0.139, 15, "LOW")
    assert s["pfz_score"] > 0.6

def test_pfz_safety_override():
    s = score_pfz(29.9, 0.139, 8, "VERY_HIGH")
    assert s["safety_override"] == "AVOID"

def test_pfz_derived_46():
    import psycopg
    c=psycopg.connect('host=localhost dbname=orca_db user=orca_app password=orca_app_pass')
    cur=c.cursor()
    cur.execute("SELECT count(*) FROM pfz_observations WHERE DATE(observation_time) BETWEEN '2026-08-15' AND '2026-09-06'")
    assert cur.fetchone()[0] == 46
    cur.execute("SELECT chlorophyll FROM ocean_observations LIMIT 1")
    assert abs(cur.fetchone()[0] - 0.139) < 0.01
