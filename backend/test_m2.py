"""M2 verification - pipeline end-to-end (docs 09_DATA_PIPELINE)."""
import asyncio, json
from datetime import datetime, timezone

# test connectors without DB/Redis/MinIO first
from app.services.ingestion.connectors.pfz_connector import PFZConnector
from app.services.ingestion.connectors.weather_connector import WeatherConnector
from app.services.ingestion.pipeline import IngestionPipeline
from app.services.ingestion.validation import PFZ_SCHEMA, WEATHER_SCHEMA
from minio import Minio
import redis

# 1. registry check
import psycopg
conn = psycopg.connect("host=localhost dbname=orca_db user=postgres password=postgres")
cur = conn.cursor()
cur.execute("SELECT id, name FROM data_sources WHERE name LIKE '%PFZ%'")
pfz_id = cur.fetchone()[0]
cur.execute("SELECT id FROM data_sources WHERE name LIKE '%Weather%'")
weather_id = cur.fetchone()[0]
print(f"registry: pfz_id={pfz_id} weather_id={weather_id}")

# registry service
from app.services.data_registry import DataRegistry
class FakeDB:
    def execute(self, q):
        cur.execute("SELECT id::text, name, provider, source_type, status, last_updated FROM data_sources ORDER BY name")
        cols = [d.name for d in cur.description]
        rows = [dict(zip(cols, r)) for r in cur.fetchall()]
        class R:
            def mappings(self): 
                class M:
                    def all(self): return rows
                return M()
        return R()
reg = DataRegistry(FakeDB())
print("list_sources:", [s["name"] for s in reg.list_sources()][:3])
print("select pfz_discovery:", [s["name"] for s in reg.select_for_intent("pfz_discovery")])

# 2. pipeline with MinIO+Redis
minio_client = Minio("localhost:9100", access_key="minioadmin", secret_key="minioadmin", secure=False)
redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)

async def run():
    pipe = IngestionPipeline(minio_client=minio_client, redis_client=redis_client, db_session=conn)
    pfz = PFZConnector(str(pfz_id))
    weather = WeatherConnector(str(weather_id))
    
    # pfz
    res_pfz = await pipe.run(pfz, PFZ_SCHEMA, params={})
    print(f"\nPFZ ingestion: processed={res_pfz['records_processed']} inserted={res_pfz['records_inserted']} failed={res_pfz['records_failed']}")
    print(f"sample: {res_pfz['data'][0].keys()}")
    
    # weather with cache test
    res_w1 = await pipe.run(weather, WEATHER_SCHEMA, params={"lat": 19.0, "lon": 72.8})
    print(f"\nWeather 1: inserted={res_w1['records_inserted']} (fetch)")
    res_w2 = await pipe.run(weather, WEATHER_SCHEMA, params={"lat": 19.0, "lon": 72.8})
    print(f"Weather 2: cached? inserted={res_w2['records_inserted']} (should be cache hit)")
    
    # 3. insert into PostGIS (M2 -> M1 tables)
    for r in res_pfz["data"]:
        cur.execute("INSERT INTO pfz_observations (source_id, observation_time, valid_from, latitude, longitude, geometry, metadata) VALUES (%s, %s, %s, %s, %s, ST_GeographyFromText(%s), %s)",
            (pfz_id, r["observation_time"], r["observation_time"], r["latitude"], r["longitude"], f"POINT({r['longitude']} {r['latitude']})", json.dumps({"sector": r.get("sector"), "sst": r.get("sst")})))
    conn.commit()
    cur.execute("SELECT count(*) FROM pfz_observations")
    print(f"\nPostGIS pfz_observations count: {cur.fetchone()[0]}")
    
    # 4. provenance check
    cur.execute("INSERT INTO ingestion_runs (data_source_id, status, records_processed, records_inserted, records_failed) VALUES (%s, 'completed', %s, %s, %s) RETURNING id", (pfz_id, res_pfz["records_processed"], res_pfz["records_inserted"], res_pfz["records_failed"]))
    print(f"ingestion_runs id: {cur.fetchone()[0]}")
    conn.commit()
    
    # 5. MinIO raw check
    objs = list(minio_client.list_objects("orca-raw-data", prefix="raw/pfz", recursive=True))
    print(f"MinIO raw objects: {len(objs)} - {[o.object_name for o in objs[:1]]}")
    
    # 6. Redis cache check
    print(f"Redis keys orca:* : {redis_client.keys('orca:*')[:3]}")

asyncio.run(run())
print("\nM2 verification DONE")
