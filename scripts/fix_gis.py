import psycopg, json, httpx, uuid
from shapely.geometry import shape, mapping, box
MUMBAI_BBOX=[72.2,18.5,73.2,19.5]
EXT_BBOX=[71.8,15.5,74.5,20.5]
conn=psycopg.connect('host=localhost dbname=orca_db user=postgres password=postgres')
cur=conn.cursor()
# alter
try:
    cur.execute('ALTER TABLE geofences ALTER COLUMN geometry TYPE geometry(Geometry,4326) USING ST_GeomFromText(ST_AsText(geometry),4326)')
    conn.commit()
    print('altered geofences to Geometry')
except Exception as e:
    print('alter', e)
    conn.rollback()
# coastline
url='https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_10m_coastline.geojson'
r=httpx.get(url, timeout=30, follow_redirects=True)
gj=r.json()
ext=box(EXT_BBOX[0],EXT_BBOX[1],EXT_BBOX[2],EXT_BBOX[3])
feats=[]
for feat in gj['features']:
    try:
        geom=shape(feat['geometry'])
        if not geom.intersects(ext):
            continue
        clipped=geom.intersection(ext)
        if clipped.is_empty:
            continue
        feats.append(mapping(clipped))
    except:
        continue
print('coast feats', len(feats))
if feats:
    cur.execute("DELETE FROM geofences WHERE name ILIKE '%coastline%'")
    for g in feats[:3]:
        cur.execute('INSERT INTO geofences (id, name, geofence_type, geometry, description) VALUES (%s,%s,%s, ST_GeomFromGeoJSON(%s), %s)', (str(uuid.uuid4()), 'Mumbai Coastline', 'coastline', json.dumps(g), 'Natural Earth 10m legit'))
    conn.commit()
    print('inserted coastline')
# EEZ
wfs='https://geo.vliz.be/geoserver/MarineRegions/wfs'
params={'service':'WFS','version':'1.0.0','request':'GetFeature','typeName':'MarineRegions:eez','outputFormat':'application/json','bbox': '72.2,18.5,73.2,19.5,urn:ogc:def:crs:EPSG:4326'}
r=httpx.get(wfs, params=params, timeout=30)
print('EEZ', r.status_code)
if r.status_code==200:
    gj=r.json()
    fs=gj.get('features', [])
    print('EEZ feats', len(fs))
    if fs:
        cur.execute("DELETE FROM maritime_boundaries WHERE name LIKE '%Mumbai%' OR name LIKE '%EEZ%'")
        for feat in fs[:3]:
            cur.execute('INSERT INTO maritime_boundaries (id, name, boundary_type, geometry, country, metadata) VALUES (%s,%s,%s, ST_GeomFromGeoJSON(%s), %s, %s)', (str(uuid.uuid4()), feat['properties'].get('GEONAME') or 'Mumbai EEZ', 'EEZ', json.dumps(feat['geometry']), 'India', json.dumps(feat['properties'])))
        conn.commit()
        print('EEZ inserted')
cur.execute('SELECT count(*) FROM geofences'); print('geofences', cur.fetchone()[0])
cur.execute('SELECT count(*) FROM maritime_boundaries'); print('maritime', cur.fetchone()[0])
conn.close()
