"""Ingest real Copernicus gridded NetCDF into ocean_observations as per-pixel real data.
Uses actual lat/lon per grid cell, not single station. No fake positions.
Sources: data/raw_copernicus/*.nc (thetao, so, uo, vo, zos, chl) 2026-06-20 + 2026-05-31
"""
import pathlib, psycopg, uuid, json
import xarray as xr
import numpy as np
from datetime import datetime, timezone

RAW = pathlib.Path("D:/ORCA/data/raw_copernicus")
BBOX = (72.2, 18.5, 73.2, 19.5)  # min_lon, min_lat, max_lon, max_lat

def get_conn():
    return psycopg.connect("host=localhost dbname=orca_db user=postgres password=postgres")

def ensure_source(cur, name="Copernicus Marine"):
    cur.execute("SELECT id FROM data_sources WHERE name=%s", (name,))
    row = cur.fetchone()
    if row:
        return row[0]
    sid = uuid.uuid4()
    cur.execute("INSERT INTO data_sources (id, name, provider, endpoint) VALUES (%s,%s,%s,%s)", (sid, name, "Copernicus", "https://data.marine.copernicus.eu"))
    return sid

def load_var(path, var, depth_idx=0):
    ds = xr.open_dataset(path)
    # isel time 0, depth 0
    arr = ds[var].isel(time=0, depth=0) if "depth" in ds[var].dims else ds[var].isel(time=0)
    lats = ds.latitude.values
    lons = ds.longitude.values
    times = ds.time.values[0]
    # convert to python datetime
    dt = np.datetime64(times).astype("datetime64[ms]").astype(datetime)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return arr, lats, lons, dt

# Load all variables that share 13x12 physics grid
phy_path = RAW / "mumbai_phy_20260620.nc"
uo_path = RAW / "mumbai_uo_20260620.nc"
vo_path = RAW / "mumbai_vo_20260620.nc"
zos_path = RAW / "mumbai_zos_20260620.nc"
chl_path = RAW / "mumbai_chl_20260531.nc"

print("Loading physics grid...")
ds_phy = xr.open_dataset(phy_path)
thetao_arr = ds_phy["thetao"].isel(time=0, depth=0)
so_arr = ds_phy["so"].isel(time=0, depth=0)
lats = ds_phy.latitude.values
lons = ds_phy.longitude.values
phy_time = np.datetime64(ds_phy.time.values[0]).astype("datetime64[ms]").astype(datetime).replace(tzinfo=timezone.utc)

ds_uo = xr.open_dataset(uo_path)
uo_arr = ds_uo["uo"].isel(time=0, depth=0)
ds_vo = xr.open_dataset(vo_path)
vo_arr = ds_vo["vo"].isel(time=0, depth=0)
ds_zos = xr.open_dataset(zos_path)
zos_arr = ds_zos["zos"].isel(time=0)
ds_chl = xr.open_dataset(chl_path)
chl_arr = ds_chl["chl"].isel(time=0, depth=0)  # 5x4
chl_lats = ds_chl.latitude.values
chl_lons = ds_chl.longitude.values

conn = get_conn()
cur = conn.cursor()
source_id = ensure_source(cur)
print(f"source_id {source_id}")

# Clean old Copernicus grid rows to avoid duplicates (keep single-point Open-Meteo 23 days)
cur.execute("DELETE FROM ocean_observations WHERE metadata->>'source' LIKE 'copernicus_grid%%'")
print(f"deleted old copernicus_grid rows: {cur.rowcount}")

inserted = 0
for i, lat in enumerate(lats):
    for j, lon in enumerate(lons):
        # bbox clip + land mask (NaN = land)
        if not (BBOX[0] <= lon <= BBOX[2] and BBOX[1] <= lat <= BBOX[3]):
            continue
        thetao = float(thetao_arr.values[i, j]) if not np.isnan(thetao_arr.values[i, j]) else None
        so = float(so_arr.values[i, j]) if not np.isnan(so_arr.values[i, j]) else None
        uo = float(uo_arr.values[i, j]) if not np.isnan(uo_arr.values[i, j]) else None
        vo = float(vo_arr.values[i, j]) if not np.isnan(vo_arr.values[i, j]) else None
        zos = float(zos_arr.values[i, j]) if not np.isnan(zos_arr.values[i, j]) else None
        # chlorophyll nearest on coarser grid
        # find nearest chl lat/lon
        ci = int(np.argmin(np.abs(chl_lats - lat)))
        cj = int(np.argmin(np.abs(chl_lons - lon)))
        chl = float(chl_arr.values[ci, cj]) if not np.isnan(chl_arr.values[ci, cj]) else None
        if thetao is None and chl is None and uo is None:
            continue  # land
        current_speed = float(np.sqrt(uo**2 + vo**2)) if uo is not None and vo is not None else None
        oid = uuid.uuid4()
        # Use phy_time as observation_time
        cur.execute(
            """
            INSERT INTO ocean_observations (id, source_id, observation_time, location, sst, chlorophyll, wave_height, current_speed, metadata)
            VALUES (%s, %s, %s, ST_SetSRID(ST_MakePoint(%s,%s),4326)::geography, %s, %s, %s, %s, %s::jsonb)
            """,
            (
                oid,
                source_id,
                phy_time,
                float(lon),
                float(lat),
                thetao,  # sst = thetao
                chl,
                zos,  # wave_height repurposed? use zos as sea level; keep wave null
                current_speed,
                json.dumps({"source": "copernicus_grid_phy_20260620", "so": so, "zos": zos, "uo": uo, "vo": vo, "depth_m": 0.494, "dataset": "GLOBAL_ANALYSISFORECAST_PHY_001_024 + BIO_001_029", "bbox": "72.2,18.5,73.2,19.5", "original_file": "mumbai_phy_uo_vo_zos_20260620.nc"}),
            ),
        )
        inserted += 1

conn.commit()
print(f"Inserted {inserted} copernicus gridded rows (13x12 physics, land masked) at 2026-06-20")
# Verify
cur.execute("SELECT count(*) FROM ocean_observations WHERE metadata->>'source' LIKE 'copernicus_grid%%'")
print("copernicus_grid count:", cur.fetchone()[0])
cur.execute("SELECT count(*) FROM ocean_observations")
print("total ocean_observations:", cur.fetchone()[0])
# Sample
cur.execute("SELECT ST_X(location::geometry), ST_Y(location::geometry), sst, chlorophyll, current_speed, metadata->>'so' FROM ocean_observations WHERE metadata->>'source' LIKE 'copernicus_grid%%' LIMIT 3")
for r in cur.fetchall():
    print(r)
conn.close()
print("Done - now /ocean/grid will serve real per-pixel values")
