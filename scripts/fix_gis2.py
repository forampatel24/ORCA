import psycopg
conn=psycopg.connect('host=localhost dbname=orca_db user=postgres password=postgres')
cur=conn.cursor()
try:
    cur.execute('ALTER TABLE maritime_boundaries ALTER COLUMN geometry TYPE geometry(Geometry,4326) USING ST_GeomFromText(ST_AsText(geometry),4326)')
    conn.commit()
    print('altered maritime')
except Exception as e:
    print('alter', e)
    conn.rollback()
try:
    cur.execute('ALTER TABLE protected_areas ALTER COLUMN geometry TYPE geometry(Geometry,4326) USING ST_GeomFromText(ST_AsText(geometry),4326)')
    conn.commit()
    print('altered protected')
except Exception as e:
    print('alter protected', e)
    conn.rollback()
cur.execute('SELECT count(*) FROM geofences'); print('geofences', cur.fetchone()[0])
cur.execute('SELECT count(*) FROM maritime_boundaries'); print('maritime', cur.fetchone()[0])
# now insert EEZ again from previous partial
import httpx, json, uuid
wfs='https://geo.vliz.be/geoserver/MarineRegions/wfs'
params={'service':'WFS','version':'1.0.0','request':'GetFeature','typeName':'MarineRegions:eez','outputFormat':'application/json','bbox': '72.2,18.5,73.2,19.5,urn:ogc:def:crs:EPSG:4326'}
r=httpx.get(wfs, params=params, timeout=30)
gj=r.json()
fs=gj.get('features', [])
print('EEZ feats', len(fs))
for feat in fs[:5]:
    print(feat['properties'].get('GEONAME'), feat['geometry']['type'])
    cur.execute('INSERT INTO maritime_boundaries (id, name, boundary_type, geometry, country, metadata) VALUES (%s,%s,%s, ST_GeomFromGeoJSON(%s), %s, %s)', (str(uuid.uuid4()), feat['properties'].get('GEONAME') or 'Mumbai EEZ', 'EEZ', json.dumps(feat['geometry']), 'India', json.dumps(feat['properties'])))
conn.commit()
print('EEZ inserted', len(fs[:3]))
cur.execute('SELECT name, ST_GeometryType(geometry) FROM maritime_boundaries LIMIT 3')
print(cur.fetchall())
conn.close()
