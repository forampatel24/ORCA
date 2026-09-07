"""Attach real Copernicus chl (fresh NRT grid) to PFZ points via nearest cell."""
import json
import numpy as np
import psycopg
import xarray as xr

conn = psycopg.connect("host=localhost dbname=orca_db user=postgres password=postgres")
cur = conn.cursor()

ds = xr.open_dataset(r"D:\Foram_TP\ORCA\data\raw_copernicus\mumbai_chl_fresh.nc")
arr = ds["chl"]
# latest time, surface depth
if "depth" in arr.dims:
    arr = arr.isel(depth=0)
arr = arr.isel(time=-1)
tval = str(ds.time.values[-1])[:10]
lats = ds.latitude.values
lons = ds.longitude.values
print("grid time:", tval, "shape:", arr.shape, "lats:", len(lats), "lons:", len(lons))

cur.execute("SELECT id, latitude, longitude FROM pfz_observations")
rows = cur.fetchall()
n_hit = n_miss = 0
for pid, lat, lon in rows:
    i = int(np.argmin(np.abs(lats - lat)))
    j = int(np.argmin(np.abs(lons - lon)))
    v = arr.values[i, j]
    if v is None or (isinstance(v, float) and np.isnan(v)):
        try:
            v = float(np.nanmean(arr.values[max(0, i - 1):i + 2, max(0, j - 1):j + 2]))
        except Exception:
            v = None
    if v is None or (isinstance(v, float) and np.isnan(v)):
        n_miss += 1
        continue
    chl = round(float(v), 4)
    cur.execute("""UPDATE pfz_observations SET metadata = metadata
        || jsonb_build_object('chlorophyll', %s::float,
                              'chlorophyll_source', 'copernicus_bgc-pft_anfc_Mumbai_' || %s,
                              'chlorophyll_note', 'nearest 0.25deg cell to PFZ point')
        WHERE id = %s""", (chl, tval, pid))
    n_hit += 1
conn.commit()
print(f"chl attached: {n_hit} miss: {n_miss}")
cur.execute("SELECT metadata->>'landing_centre', metadata->>'sst', metadata->>'chlorophyll' FROM pfz_observations ORDER BY latitude DESC LIMIT 8")
for r in cur.fetchall():
    print(" ", r)
conn.close()
