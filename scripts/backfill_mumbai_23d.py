"""Backfill Mumbai weather+ocean 23 days (ending today) into DOCKER orca-postgres.

Weather: Open-Meteo Archive (archive-api.open-meteo.com), noon UTC daily.
Ocean: Open-Meteo Marine with past_days, noon UTC daily SST/wave.
Connects via app.database.connection.psycopg_conninfo() (env-driven port).
Idempotent: deletes existing rows in window first.
"""
import sys
import uuid
import json
from datetime import date, timedelta

sys.path.insert(0, r"D:\Foram_TP\ORCA\backend")

import httpx
import psycopg
from app.database.connection import psycopg_conninfo

LAT, LON = 19.076, 72.877
DAYS = 23
END = date.today()
START = END - timedelta(days=DAYS - 1)
print(f"Window {START} -> {END} ({DAYS} days) Mumbai {LAT},{LON}")


def noon_value(times, vals, day_iso):
    for t, v in zip(times, vals):
        if t.startswith(day_iso) and t[11:13] == "12" and v is not None:
            return v
    # fallback: first non-null of that day
    for t, v in zip(times, vals):
        if t.startswith(day_iso) and v is not None:
            return v
    return None


def main():
    weather_rows, ocean_rows = [], []
    with httpx.Client(timeout=30) as c:
        wr = c.get("https://archive-api.open-meteo.com/v1/archive", params={
            "latitude": LAT, "longitude": LON,
            "start_date": START.isoformat(), "end_date": END.isoformat(),
            "hourly": "temperature_2m,wind_speed_10m,wind_direction_10m,precipitation,relative_humidity_2m,surface_pressure",
            "timezone": "UTC",
        })
        wr.raise_for_status()
        h = wr.json().get("hourly", {})
        for i in range(DAYS):
            day = (START + timedelta(days=i)).isoformat()
            weather_rows.append({
                "day": day,
                "temperature": noon_value(h.get("time", []), h.get("temperature_2m", []), day),
                "wind_speed": noon_value(h.get("time", []), h.get("wind_speed_10m", []), day),
                "wind_direction": noon_value(h.get("time", []), h.get("wind_direction_10m", []), day),
                "rainfall": noon_value(h.get("time", []), h.get("precipitation", []), day),
                "humidity": noon_value(h.get("time", []), h.get("relative_humidity_2m", []), day),
                "pressure": noon_value(h.get("time", []), h.get("surface_pressure", []), day),
            })
        print(f"weather days fetched: {len(weather_rows)}")

        mr = c.get("https://marine-api.open-meteo.com/v1/marine", params={
            "latitude": LAT, "longitude": LON,
            "hourly": "wave_height,wave_period,wave_direction,sea_surface_temperature",
            "past_days": DAYS, "forecast_days": 1, "timezone": "UTC",
        })
        mr.raise_for_status()
        mh = mr.json().get("hourly", {})
        for i in range(DAYS):
            day = (START + timedelta(days=i)).isoformat()
            ocean_rows.append({
                "day": day,
                "sst": noon_value(mh.get("time", []), mh.get("sea_surface_temperature", []), day),
                "wave_height": noon_value(mh.get("time", []), mh.get("wave_height", []), day),
                "wave_period": noon_value(mh.get("time", []), mh.get("wave_period", []), day),
            })
        print(f"ocean days fetched: {len(ocean_rows)}")

    conn = psycopg.connect(psycopg_conninfo())
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM data_sources WHERE name IN ('IMD Weather','INCOIS OSF')")
    src = {n: i for i, n in cur.fetchall()}
    weather_id, ocean_id = src.get("IMD Weather"), src.get("INCOIS OSF")
    print("source ids:", weather_id, ocean_id)

    cur.execute("DELETE FROM weather_observations WHERE observation_time::date BETWEEN %s AND %s",
                (START.isoformat(), END.isoformat()))
    print("deleted weather in window:", cur.rowcount)
    for r in weather_rows:
        cur.execute("""
            INSERT INTO weather_observations
            (id, source_id, observation_time, forecast_time, location, temperature,
             wind_speed, wind_direction, rainfall, humidity, pressure, metadata)
            VALUES (%s,%s,%s,%s, ST_GeographyFromText(%s), %s,%s,%s,%s,%s,%s,%s)
        """, (str(uuid.uuid4()), weather_id, f"{r['day']}T12:00:00+00:00", f"{r['day']}T12:00:00+00:00",
              f"POINT({LON} {LAT})", r["temperature"], r["wind_speed"], r["wind_direction"],
              r["rainfall"], r["humidity"], r["pressure"],
              json.dumps({"source": "open-meteo_archive_noon_utc", "backfill_23d": True})))

    cur.execute("DELETE FROM ocean_observations WHERE observation_time::date BETWEEN %s AND %s"
                " AND (metadata->>'backfill_23d' = 'true' OR metadata->>'source' = 'open-meteo_marine_mumbai')",
                (START.isoformat(), END.isoformat()))
    print("deleted ocean in window:", cur.rowcount)
    for r in ocean_rows:
        cur.execute("""
            INSERT INTO ocean_observations
            (id, source_id, observation_time, location, sst, chlorophyll,
             wave_height, wave_period, metadata)
            VALUES (%s,%s,%s, ST_GeographyFromText(%s), %s,%s,%s,%s,%s)
        """, (str(uuid.uuid4()), ocean_id, f"{r['day']}T12:00:00+00:00",
              f"POINT({LON} {LAT})", r["sst"], None, r["wave_height"], r["wave_period"],
              json.dumps({"source": "open-meteo_marine_mumbai", "backfill_23d": True})))
    conn.commit()
    cur.execute("SELECT count(*), min(observation_time)::text, max(observation_time)::text FROM weather_observations")
    print("WEATHER now:", cur.fetchone())
    cur.execute("SELECT count(*), min(observation_time)::text, max(observation_time)::text FROM ocean_observations")
    print("OCEAN now:", cur.fetchone())
    conn.close()


if __name__ == "__main__":
    main()
