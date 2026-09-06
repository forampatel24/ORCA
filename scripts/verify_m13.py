import psycopg, json
c=psycopg.connect('host=localhost dbname=orca_db user=orca_app password=orca_app_pass')
cur=c.cursor()
for t in ['maritime_boundaries','protected_areas','geofences','weather_observations','ocean_observations','pfz_observations','knowledge_documents','cmfri_landings']:
    try:
        cur.execute(f'SELECT count(*) FROM {t}')
        print(t, cur.fetchone()[0])
    except Exception as e:
        print(t, 'err', e)
        c.rollback()
print('--- spatial legit ---')
try:
    cur.execute("SELECT name FROM maritime_boundaries WHERE ST_Intersects(geometry, ST_GeomFromText('POINT(72.877 19.076)',4326)) LIMIT 1")
    print('EEZ intersects Mumbai', cur.fetchone())
except Exception as e:
    print('EEZ', e)
    c.rollback()
try:
    cur.execute("SELECT name FROM geofences WHERE ST_DWithin(geometry::geography, ST_GeographyFromText('POINT(72.877 19.076)'), 20000) LIMIT 1")
    print('Geofence 20km', cur.fetchone())
except Exception as e:
    print('geofence', e)
    c.rollback()
c.close()
from app.tools.weather import get_weather
print('weather tool', get_weather(19.076,72.877))
from app.tools.ocean import get_ocean
print('ocean tool', get_ocean(19.076,72.877))
from app.tools.geospatial import check_geofence
print('geofence tool', check_geofence(19.076,72.877))
from app.services.ingestion.connectors.gfw_connector import GFWConnector
import asyncio
async def t():
    conn=GFWConnector('test')
    data=await conn.fetch(bbox=[72.2,18.5,73.2,19.5], limit=2)
    print('GFW legit Mumbai', len(data), str(data[0])[:400] if data else 'no vessel (legit: bbox empty)')
asyncio.run(t())
