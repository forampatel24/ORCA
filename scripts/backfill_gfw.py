"""Backfill GFW v3 fishing events (Maharashtra bbox) into vessel_tracks.

Uses live GFWConnector (v3 gateway POST). Idempotent: deletes rows for the
same event_ids first. Connects via psycopg_conninfo (env port).
"""
import sys
import asyncio
import uuid
import json

sys.path.insert(0, r"D:\Foram_TP\ORCA\backend")

import psycopg
from app.database.connection import psycopg_conninfo
from app.services.ingestion.connectors.gfw_connector import GFWConnector


async def main():
    conn = psycopg.connect(psycopg_conninfo())
    cur = conn.cursor()
    cur.execute("SELECT id FROM data_sources WHERE name='GFW Fishing Events' LIMIT 1")
    row = cur.fetchone()
    src_id = row[0] if row else None
    print("source GFW Fishing Events:", src_id)

    c = GFWConnector(str(src_id))
    rows = await c.fetch(limit=50)
    print(f"live GFW rows: {len(rows)}")
    if not rows:
        print("NO ROWS - token missing or API unreachable, DB untouched")
        return

    for r in rows:
        md = dict(r.get("metadata", {}))
        md["source"] = r.get("source")
        eid = md.get("event_id")
        if eid:
            cur.execute("DELETE FROM vessel_tracks WHERE metadata->>'event_id' = %s", (eid,))
        cur.execute("""
            INSERT INTO vessel_tracks
            (id, source_id, observation_time, latitude, longitude, location,
             vessel_id, vessel_name, event_type, metadata)
            VALUES (%s,%s,%s,%s,%s, ST_GeographyFromText(%s), %s,%s,%s,%s::jsonb)
        """, (str(uuid.uuid4()), src_id, r.get("observation_time"),
              r["latitude"], r["longitude"],
              f"POINT({r['longitude']} {r['latitude']})",
              r.get("vessel_id"), r.get("vessel_name"), r.get("type"),
              json.dumps(md)))
    conn.commit()
    cur.execute("SELECT count(*) FROM vessel_tracks")
    print("vessel_tracks now:", cur.fetchone()[0])
    cur.execute("SELECT vessel_name, latitude, longitude, observation_time::text FROM vessel_tracks ORDER BY observation_time LIMIT 5")
    for v in cur.fetchall():
        print(" ", v)
    conn.close()


if __name__ == "__main__":
    asyncio.run(main())
