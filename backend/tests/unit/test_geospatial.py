"""Geospatial tests - updated for Mumbai legit 5 EEZ 1 coastline 23 days."""
from app.tools.geospatial import check_geofence, calculate_distance

def test_geofence_inside():
    r = check_geofence(19.076, 72.877)
    assert r["nearest_geofence"] == "Mumbai Coastline"
    assert r["distance_to_nearest_km"] < 10

def test_geofence_outside():
    r = check_geofence(10.0, 70.0)
    assert r["inside_geofence"] is None

def test_distance():
    d = calculate_distance(19.0,72.8,19.1,72.5)
    assert 30 < d < 35

def test_eez_mumbai_exists():
    import psycopg
    c=psycopg.connect('host=localhost dbname=orca_db user=orca_app password=orca_app_pass')
    cur=c.cursor()
    cur.execute("SELECT count(*) FROM maritime_boundaries")
    assert cur.fetchone()[0] >= 3
    cur.execute("SELECT count(*) FROM geofences")
    assert cur.fetchone()[0] >= 1

def test_weather_23_days():
    import psycopg
    c=psycopg.connect('host=localhost dbname=orca_db user=orca_app password=orca_app_pass')
    cur=c.cursor()
    cur.execute("SELECT count(*) FROM weather_observations WHERE DATE(observation_time) BETWEEN '2026-08-15' AND '2026-09-06'")
    assert cur.fetchone()[0] == 23

def test_ocean_chl_legit():
    import psycopg
    c=psycopg.connect('host=localhost dbname=orca_db user=orca_app password=orca_app_pass')
    cur=c.cursor()
    cur.execute("SELECT chlorophyll FROM ocean_observations WHERE chlorophyll IS NOT NULL LIMIT 1")
    row=cur.fetchone()
    assert row and abs(row[0] - 0.139) < 0.02
