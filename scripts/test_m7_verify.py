import psycopg
c=psycopg.connect('host=localhost dbname=orca_db user=postgres password=postgres')
cur=c.cursor()
cur.execute('SELECT name FROM protected_areas')
print('protected', [r[0] for r in cur.fetchall()])
cur.execute("SELECT ST_Contains(geometry, ST_GeomFromText('POINT(78.5 9.0)',4326)) FROM protected_areas WHERE name='Gulf of Mannar MPA'")
print('Gulf contains 78.5,9.0', cur.fetchone()[0])
cur.execute("SELECT ST_DWithin(geometry::geography, ST_GeographyFromText('POINT(72.8 19.0)'), 50000) FROM maritime_boundaries WHERE name='India EEZ'")
print('EEZ 50km Mumbai', cur.fetchone()[0])
from app.tools.geospatial import check_geofence
print('check 78.5,9.0', check_geofence(78.5,9.0))
print('check 19.0,72.8', check_geofence(19.0,72.8))
from minio import Minio
m=Minio('localhost:9100', access_key='minioadmin', secret_key='minioadmin', secure=False)
print('minio raster', [o.object_name for o in m.list_objects('orca-raster', recursive=True)])
cur.execute('SELECT year, landings_tonnes FROM cmfri_landings WHERE state=%s ORDER BY year', ('Maharashtra',))
print('cmfri Maharashtra', cur.fetchall())
