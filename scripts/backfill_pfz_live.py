"""Backfill PFZ live INCOIS SEC002 (Mumbai bbox) into DOCKER orca-postgres.

Uses fixed PFZConnector (session + DMS parse). Idempotent: deletes today's
INCOIS rows first, then inserts. Connects via psycopg_conninfo (env port).
"""
import sys
import asyncio
import uuid
import json

sys.path.insert(0, r"D:\Foram_TP\ORCA\backend")

import psycopg
from app.database.connection import psycopg_conninfo
from app.services.ingestion.connectors.pfz_connector import PFZConnector


async def main():
    conn = psycopg.connect(psycopg_conninfo())
    cur = conn.cursor()
    cur.execute("SELECT id FROM data_sources WHERE name='INCOIS PFZ' LIMIT 1")
    src_id = cur.fetchone()[0]
    print("source INCOIS PFZ:", src_id)

    c = PFZConnector(str(src_id))
    rows = await c.fetch()
    print(f"live INCOIS Mumbai rows: {len(rows)}")
    if not rows:
        print("NO ROWS - ban/adverse day or fetch failed, DB untouched")
        return

    obs_day = rows[0]["observation_time"][:10]
    cur.execute("DELETE FROM pfz_observations WHERE metadata->>'sector_total' IS NOT NULL"
                " AND observation_time::date = %s", (obs_day,))
    print("deleted same-day INCOIS rows:", cur.rowcount)

    for r in rows:
        md = dict(r.get("metadata", {}))
        md["source"] = r.get("source")
        cur.execute("""
            INSERT INTO pfz_observations
            (id, source_id, observation_time, valid_from, valid_to,
             latitude, longitude, geometry, metadata)
            VALUES (%s,%s,%s,%s,%s,%s,%s, ST_GeographyFromText(%s), %s::jsonb)
        """, (str(uuid.uuid4()), src_id, r["observation_time"],
              r.get("valid_from"), r.get("valid_to"),
              r["latitude"], r["longitude"],
              f"POINT({r['longitude']} {r['latitude']})",
              json.dumps(md)))
    conn.commit()
    cur.execute("SELECT count(*) FROM pfz_observations")
    print("PFZ now:", cur.fetchone()[0])
    cur.execute("SELECT landing_centre FROM (SELECT metadata->>'landing_centre' AS landing_centre FROM pfz_observations) t LIMIT 5")
    print("sample:", cur.fetchall())
    conn.close()


if __name__ == "__main__":
    asyncio.run(main())
