"""Ocean tools."""
import psycopg
def get_ocean(lat: float, lon: float):
    """SST/chlorophyll/wave mock."""
    try:
        conn = psycopg.connect("host=localhost dbname=orca_db user=postgres password=postgres")
        cur = conn.cursor()
        cur.execute("SELECT sst, chlorophyll FROM ocean_observations ORDER BY observation_time DESC LIMIT 1")
        r = cur.fetchone()
        conn.close()
        if r and r[0]:
            return {"sst": r[0], "chlorophyll": r[1], "source": "ocean_observations"}
    except: pass
    return {"sst": 28.2, "chlorophyll": 0.8, "wave_height": 1.2, "source": "mock_pfZ"}
