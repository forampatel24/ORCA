import os
for line in open(r"D:\Foram_TP\ORCA\backend\.env", encoding="utf-8"):
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        os.environ[k.strip()] = v.strip()
import copernicusmarine
try:
    fp = copernicusmarine.subset(
        dataset_id="cmems_mod_glo_bgc-pft_anfc_0.25deg_P1D-m", variables=["chl"],
        start_datetime="2026-09-01T00:00:00", end_datetime="2026-09-07T23:59:59",
        minimum_depth=0, maximum_depth=1,
        minimum_longitude=71.8, maximum_longitude=74.5,
        minimum_latitude=15.5, maximum_latitude=20.5,
        output_filename="mumbai_chl_fresh.nc",
        output_directory=r"D:\Foram_TP\ORCA\data\raw_copernicus")
    print("OK chl ->", fp)
except Exception as e:
    print("FAIL chl", str(e)[:500])
