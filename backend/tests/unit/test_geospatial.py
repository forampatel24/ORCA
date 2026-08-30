"""Geospatial tests - docs 17 TEST-005."""
from app.tools.geospatial import check_geofence, calculate_distance

def test_geofence_inside():
    r = check_geofence(19.0, 72.8)
    assert r["inside_geofence"] == "Test MPA Mumbai"

def test_geofence_outside():
    r = check_geofence(10.0, 70.0)
    assert r["inside_geofence"] is None

def test_distance():
    d = calculate_distance(19.0,72.8,19.1,72.5)
    assert 30 < d < 35

def test_eez_contains():
    import psycopg
    c=psycopg.connect('host=localhost dbname=orca_db user=orca_app password=orca_app_pass')
    cur=c.cursor()
    cur.execute("SELECT ST_Contains(geometry, ST_GeomFromText('POINT(72.8 19.0)',4326)) FROM maritime_boundaries WHERE name='India EEZ'")
    assert cur.fetchone()[0] is True
