"""Fix EEZ: refetch MarineRegions WFS with correct axis order, clip to Maharashtra.

Previous ingest used bbox '...urn:ogc:def:crs:EPSG:4326' which made GeoServer
return lat/lon-swapped geometries (centroids at poles). This refetches with
plain EPSG:4326 (lon,lat order for WFS 1.0.0), sanity-checks centroids inside
the extended Maharashtra bbox, clips, and replaces maritime_boundaries.
"""
import json
import uuid

import httpx
import psycopg
from shapely.geometry import shape, mapping, box

MUMBAI_BBOX = [72.2, 18.5, 73.2, 19.5]
EXT_BBOX = [71.8, 15.5, 74.5, 20.5]
ext_geom = box(EXT_BBOX[0], EXT_BBOX[1], EXT_BBOX[2], EXT_BBOX[3])

WFS = "https://geo.vliz.be/geoserver/MarineRegions/wfs"
params = {
    "service": "WFS", "version": "1.0.0", "request": "GetFeature",
    "typeName": "MarineRegions:eez", "outputFormat": "application/json",
    # WFS 1.0.0 + EPSG:4326 => lon,lat order. NO urn suffix (that flips axes).
    "bbox": f"{MUMBAI_BBOX[0]},{MUMBAI_BBOX[1]},{MUMBAI_BBOX[2]},{MUMBAI_BBOX[3]}",
    "srsName": "EPSG:4326",
}

r = httpx.get(WFS, params=params, timeout=40)
r.raise_for_status()
gj = r.json()
feats = gj.get("features", [])
print(f"WFS features: {len(feats)}")

kept = []
for feat in feats:
    try:
        geom = shape(feat["geometry"])
        c = geom.centroid
        # sanity: centroid lon 60-80, lat 5-25 (Indian Ocean)
        if not (60 <= c.x <= 80 and 5 <= c.y <= 25):
            print(f"  SKIP swapped/bad centroid {c.x:.2f},{c.y:.2f}")
            continue
        clipped = geom.intersection(ext_geom)
        if clipped.is_empty:
            print("  SKIP no overlap with Maharashtra ext bbox")
            continue
        kept.append((feat, clipped))
    except Exception as e:
        print("  SKIP parse error", e)
print(f"kept: {len(kept)}")

conn = psycopg.connect("host=localhost dbname=orca_db user=postgres password=postgres")
cur = conn.cursor()
cur.execute("DELETE FROM maritime_boundaries")
for feat, clipped in kept:
    props = feat.get("properties", {})
    name = props.get("GEONAME") or props.get("geaname") or "India EEZ (Maharashtra clip)"
    cur.execute(
        "INSERT INTO maritime_boundaries (id, name, boundary_type, geometry, country, metadata)"
        " VALUES (%s,%s,%s, ST_GeomFromGeoJSON(%s), %s, %s)",
        (str(uuid.uuid4()), f"{name} - Maharashtra clip", "EEZ",
         json.dumps(mapping(clipped)), props.get("TERRITORY1") or "India",
         json.dumps({"bbox": "maharashtra-ext", "wfs": "MarineRegions eez 1.0.0"})))
conn.commit()
cur.execute("SELECT name, ST_AsText(ST_Centroid(geometry)) FROM maritime_boundaries")
for row in cur.fetchall():
    print(" ", row)
conn.close()
print("EEZ fix done")
