"""Live Mumbai ingest - replaces dummy with Open-Meteo live for demo. No Kafka."""
import asyncio, sys, json, uuid
sys.path.insert(0, "D:/Foram_TP/ORCA/backend")
import psycopg
from app.services.ingestion.connectors.weather_connector import WeatherConnector
from app.services.ingestion.connectors.ocean_connector import OceanConnector

async def main():
    conn = psycopg.connect("host=localhost dbname=orca_db user=postgres password=postgres")
    cur = conn.cursor()
    # get source ids
    cur.execute("SELECT id FROM data_sources WHERE name='IMD Weather' LIMIT 1")
    weather_id = cur.fetchone()[0]
    cur.execute("SELECT id FROM data_sources WHERE name='INCOIS OSF' LIMIT 1")
    ocean_id = cur.fetchone()[0]
    print(f"weather_id {weather_id} ocean_id {ocean_id}")

    # fetch live
    wc = WeatherConnector(str(weather_id))
    oc = OceanConnector(str(ocean_id))
    weather_data = await wc.fetch(lat=19.076, lon=72.877)
    ocean_data = await oc.fetch(lat=19.076, lon=72.877)
    print(f"Fetched weather {len(weather_data)} ocean {len(ocean_data)}")
    for r in weather_data:
        print("  W", r)
    for r in ocean_data:
        print("  O", r)

    # insert weather
    for r in weather_data:
        cur.execute("""
            INSERT INTO weather_observations (id, source_id, observation_time, forecast_time, location, temperature, wind_speed, wind_direction, rainfall, humidity, pressure, metadata)
            VALUES (%s,%s,%s,%s, ST_GeographyFromText(%s), %s,%s,%s,%s,%s,%s,%s)
        """, (
            str(uuid.uuid4()), weather_id, r["observation_time"], r["forecast_time"],
            f"POINT({r['longitude']} {r['latitude']})",
            r.get("temperature"), r.get("wind_speed"), r.get("wind_direction"), r.get("rainfall"), r.get("humidity"), r.get("pressure"),
            json.dumps({"source": r.get("source"), "live": True})
        ))
    # insert ocean
    for r in ocean_data:
        cur.execute("""
            INSERT INTO ocean_observations (id, source_id, observation_time, location, sst, chlorophyll, wave_height, wave_period, metadata)
            VALUES (%s,%s,%s, ST_GeographyFromText(%s), %s,%s,%s,%s,%s)
        """, (
            str(uuid.uuid4()), ocean_id, r["observation_time"],
            f"POINT({r['longitude']} {r['latitude']})",
            r.get("sst"), r.get("chlorophyll"), r.get("wave_height"), r.get("wave_period"),
            json.dumps({"source": r.get("source"), "live": True})
        ))
    conn.commit()
    cur.execute("SELECT COUNT(*) FROM weather_observations")
    print("weather total", cur.fetchone()[0])
    cur.execute("SELECT COUNT(*) FROM ocean_observations")
    print("ocean total", cur.fetchone()[0])
    # verify tools
    from app.tools.weather import get_weather
    from app.tools.ocean import get_ocean
    print("tool weather", get_weather(19.076, 72.877))
    print("tool ocean", get_ocean(19.076, 72.877))
    conn.close()

asyncio.run(main())
print("Live Mumbai ingest DONE")
