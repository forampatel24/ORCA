import os
for line in open(r"D:\Foram_TP\ORCA\backend\.env", encoding="utf-8"):
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        os.environ[k.strip()] = v.strip()
import copernicusmarine
for dsid in ["cmems_mod_glo_phy_my_0.083deg_P1D-m", "cmems_mod_glo_bgc_my_0.25deg_P1D-m"]:
    try:
        d = copernicusmarine.describe(dataset_id=dsid)
        dd = d.model_dump()
        prods = dd.get("products", [])
        vers = prods[0].get("datasets", []) if prods else []
        print("=" * 10, dsid)
        for v in vers[:3]:
            print("  dataset:", v.get("dataset_id"))
        import json
        full = json.dumps(dd, default=str)
        import re
        names = sorted(set(re.findall(r'"short_name"\s*:\s*"([^"]+)"', full)))
        print("  vars:", names[:40])
    except Exception as e:
        print(dsid, "FAIL", str(e)[:300])
