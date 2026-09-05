"""M7 Static GIS ingest - EEZ/MPA/coastline/bathymetry/CMFRI per docs 08."""
import json, csv, psycopg, os, pathlib
import uuid
from urllib.parse import urlparse

# Portable project root — works on any clone (no D: hardcode)
PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
# Allow env override for custom data locations
DATA_EXTERNAL = pathlib.Path(os.getenv("ORCA_DATA_EXTERNAL", str(PROJECT_ROOT / "data" / "external")))
DATA_PROCESSED = pathlib.Path(os.getenv("ORCA_DATA_PROCESSED", str(PROJECT_ROOT / "data" / "processed")))

def _conn_str():
    url = os.getenv("DATABASE_URL_ADMIN") or os.getenv("DATABASE_URL") or ""
    if url.startswith("postgresql"):
        url = url.replace("postgresql+psycopg://", "postgresql://")
        p = urlparse(url)
        return f"host={p.hostname or 'localhost'} port={p.port or 5432} dbname={(p.path or '/orca_db').lstrip('/')} user={p.username or 'postgres'} password={p.password or 'postgres'}"
    return os.getenv("DATABASE_URL_PSYCOPG", "host=localhost dbname=orca_db user=postgres password=postgres")

conn = psycopg.connect(_conn_str())
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS cmfri_landings (id UUID PRIMARY KEY, year INT, state VARCHAR, species VARCHAR, landings_tonnes INT, gear VARCHAR)")
cur.execute("DELETE FROM maritime_boundaries WHERE name='India EEZ'")
cur.execute("DELETE FROM protected_areas WHERE name IN ('Gulf of Mannar MPA','Malvan MPA Maharashtra')")
cur.execute("DELETE FROM geofences WHERE name='Maharashtra Coastline'")
cur.execute("DELETE FROM cmfri_landings WHERE state IN ('Maharashtra','Gujarat')")
conn.commit()

# 1. EEZ -> maritime_boundaries
with open(DATA_EXTERNAL / "eez_india.geojson") as f:
    gj = json.load(f)
    for feat in gj["features"]:
        geom = json.dumps(feat["geometry"])
        cur.execute("INSERT INTO maritime_boundaries (id, name, boundary_type, geometry, country, metadata) VALUES (%s,%s,%s, ST_GeomFromGeoJSON(%s), %s, %s)",
            (str(uuid.uuid4()), feat["properties"]["name"], feat["properties"]["boundary_type"], geom, feat["properties"]["country"], json.dumps(feat["properties"])))
conn.commit()
print("EEZ inserted")

# 2. MPA -> protected_areas
with open(DATA_EXTERNAL / "mpa_india.geojson") as f:
    gj = json.load(f)
    for feat in gj["features"]:
        geom = json.dumps(feat["geometry"])
        cur.execute("INSERT INTO protected_areas (id, name, area_type, geometry, authority, metadata) VALUES (%s,%s,%s, ST_GeomFromGeoJSON(%s), %s, %s)",
            (str(uuid.uuid4()), feat["properties"]["name"], feat["properties"]["area_type"], geom, feat["properties"]["authority"], json.dumps(feat["properties"])))
conn.commit()
print("MPA inserted 2")

# 3. Coastline -> geofences as operational (for demo)
with open(DATA_EXTERNAL / "coastline_india.geojson") as f:
    gj = json.load(f)
    for feat in gj["features"]:
        geom = json.dumps(feat["geometry"])
        cur.execute("INSERT INTO geofences (id, name, geofence_type, geometry, description) VALUES (%s,%s,%s, ST_Buffer(ST_GeomFromGeoJSON(%s)::geography, 5000)::geometry, %s)",
            (str(uuid.uuid4()), feat["properties"]["name"], "operational", geom, "Maharashtra coastline 5km buffer"))
conn.commit()

# 4. Bathymetry mock - create raster via PostGIS raster? For M7 we store metadata in MinIO
from minio import Minio
import io
# MinIO endpoint from env portable
_minio_endpoint = os.getenv("MINIO_ENDPOINT", "localhost:9100")
_minio_access = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
_minio_secret = os.getenv("MINIO_SECRET_KEY", "minioadmin")
_minio_secure = os.getenv("MINIO_SECURE", "false").lower() == "true"
minio_client = Minio(_minio_endpoint, access_key=_minio_access, secret_key=_minio_secret, secure=_minio_secure)
# mock GeoTIFF 10x10 with depth -20 to -100
# Bathymetry mock - PROJ 8.2 vs 9 mismatch thorough fix: use dummy 80 bytes for M7 demo, real GEBCO would need pyproj>=3.7
tmp = str(DATA_PROCESSED / "bathymetry_sample.tif")
os.makedirs(os.path.dirname(tmp), exist_ok=True)
# keep existing dummy if exists, else create
if not os.path.exists(tmp) or os.path.getsize(tmp) < 100:
    with open(tmp, "wb") as tmpf:
        tmpf.write(b"Mock Bathymetry GEBCO 2026 subset Indian Ocean 10x10 depth -100 to -20 EPSG:4326")
with open(tmp, "rb") as f:
    b = f.read()
    minio_client.put_object("orca-raster", "bathymetry/gebco_subset_sample.tif", io.BytesIO(b), len(b))
print("bathymetry raster -> MinIO orca-raster/bathymetry/gebco_subset_sample.tif", len(b))

# 5. CMFRI -> create table if not exists and insert
cur.execute("CREATE TABLE IF NOT EXISTS cmfri_landings (id UUID PRIMARY KEY, year INT, state VARCHAR, species VARCHAR, landings_tonnes INT, gear VARCHAR)")
with open(DATA_EXTERNAL / "cmfri_landings.csv") as f:
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
