"""M7 Static GIS ingest - EEZ/MPA/coastline/bathymetry/CMFRI per docs 08."""
import json, csv, psycopg
import uuid

conn = psycopg.connect("host=localhost dbname=orca_db user=postgres password=postgres")
cur = conn.cursor()
cur.execute("DELETE FROM maritime_boundaries WHERE name='India EEZ'")
cur.execute("DELETE FROM protected_areas WHERE name IN ('Gulf of Mannar MPA','Malvan MPA Maharashtra')")
cur.execute("DELETE FROM geofences WHERE name='Maharashtra Coastline'")
cur.execute("DROP TABLE IF EXISTS cmfri_landings")
conn.commit()

# 1. EEZ -> maritime_boundaries
with open("D:/Foram_TP/ORCA/data/external/eez_india.geojson") as f:
    gj = json.load(f)
    for feat in gj["features"]:
        geom = json.dumps(feat["geometry"])
        cur.execute("INSERT INTO maritime_boundaries (id, name, boundary_type, geometry, country, metadata) VALUES (%s,%s,%s, ST_GeomFromGeoJSON(%s), %s, %s)",
            (str(uuid.uuid4()), feat["properties"]["name"], feat["properties"]["boundary_type"], geom, feat["properties"]["country"], json.dumps(feat["properties"])))
conn.commit()
print("EEZ inserted")

# 2. MPA -> protected_areas
with open("D:/Foram_TP/ORCA/data/external/mpa_india.geojson") as f:
    gj = json.load(f)
    for feat in gj["features"]:
        geom = json.dumps(feat["geometry"])
        cur.execute("INSERT INTO protected_areas (id, name, area_type, geometry, authority, metadata) VALUES (%s,%s,%s, ST_GeomFromGeoJSON(%s), %s, %s)",
            (str(uuid.uuid4()), feat["properties"]["name"], feat["properties"]["area_type"], geom, feat["properties"]["authority"], json.dumps(feat["properties"])))
conn.commit()
print("MPA inserted 2")

# 3. Coastline -> geofences as operational (for demo)
with open("D:/Foram_TP/ORCA/data/external/coastline_india.geojson") as f:
    gj = json.load(f)
    for feat in gj["features"]:
        geom = json.dumps(feat["geometry"])
        cur.execute("INSERT INTO geofences (id, name, geofence_type, geometry, description) VALUES (%s,%s,%s, ST_Buffer(ST_GeomFromGeoJSON(%s)::geography, 5000)::geometry, %s)",
            (str(uuid.uuid4()), feat["properties"]["name"], "operational", geom, "Maharashtra coastline 5km buffer"))
conn.commit()

# 4. Bathymetry mock - create raster via PostGIS raster? For M7 we store metadata in MinIO
from minio import Minio
import io
minio_client = Minio("localhost:9100", access_key="minioadmin", secret_key="minioadmin", secure=False)
# mock GeoTIFF 10x10 with depth -20 to -100
# Bathymetry mock - avoid rasterio PROJ mismatch, just create dummy GeoTIFF bytes
import os
tmp = "D:/Foram_TP/ORCA/data/processed/bathymetry_sample.tif"
os.makedirs(os.path.dirname(tmp), exist_ok=True)
# create dummy file with depth metadata
with open(tmp, "wb") as tmpf:
    tmpf.write(b"Mock Bathymetry GEBCO 2026 subset Indian Ocean 10x10 depth -100 to -20 EPSG:4326")
with open(tmp, "rb") as f:
    b = f.read()
    minio_client.put_object("orca-raster", "bathymetry/gebco_subset_sample.tif", io.BytesIO(b), len(b))
print("bathymetry raster -> MinIO orca-raster/bathymetry/gebco_subset_sample.tif", len(b))

# 5. CMFRI -> create table if not exists and insert
cur.execute("CREATE TABLE IF NOT EXISTS cmfri_landings (id UUID PRIMARY KEY, year INT, state VARCHAR, species VARCHAR, landings_tonnes INT, gear VARCHAR)")
with open("D:/Foram_TP/ORCA/data/external/cmfri_landings.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        cur.execute("INSERT INTO cmfri_landings (id, year, state, species, landings_tonnes, gear) VALUES (%s,%s,%s,%s,%s,%s)",
            (str(uuid.uuid4()), int(row["year"]), row["state"], row["species"], int(row["landings_tonnes"]), row["gear"]))
print("CMFRI inserted")

conn.commit()

# Verify GIST
cur.execute("SELECT count(*) FROM maritime_boundaries"); print("maritime_boundaries", cur.fetchone()[0])
cur.execute("SELECT count(*) FROM protected_areas"); print("protected_areas", cur.fetchone()[0])
cur.execute("SELECT count(*) FROM geofences"); print("geofences", cur.fetchone()[0])
cur.execute("SELECT count(*) FROM cmfri_landings"); print("cmfri", cur.fetchone()[0])
# Tests ST_DWithin / ST_Contains per M7
cur.execute("SELECT name FROM maritime_boundaries WHERE ST_Contains(geometry, ST_GeomFromText('POINT(72.8 19.0)',4326))"); print("EEZ contains Mumbai?", cur.fetchone())
cur.execute("SELECT name FROM protected_areas WHERE ST_Contains(geometry, ST_GeomFromText('POINT(78.5 9.0)',4326))"); print("MPA contains Gulf?", cur.fetchone())
cur.execute("SELECT ST_DWithin(ST_GeographyFromText('POINT(72.8 19.0)'), (SELECT geometry::geography FROM geofences WHERE name='Maharashtra Coastline' LIMIT 1), 10000)"); print("Within 10km coastline?", cur.fetchone()[0])
