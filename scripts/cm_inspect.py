import xarray as xr, glob
for f in sorted(glob.glob(r"D:\Foram_TP\ORCA\data\raw_copernicus\*.nc")):
    ds = xr.open_dataset(f)
    print("=" * 20, f.split("\\")[-1])
    print("  vars:", list(ds.data_vars)[:12])
    print("  time:", ds.time.values[0], "->", ds.time.values[-1])
    for k in ("id", "dataset_id", "product_id", "title", "source", "history"):
        if k in ds.attrs:
            print(f"  {k}:", str(ds.attrs[k])[:150])
    ds.close()
