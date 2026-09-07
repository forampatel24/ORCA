"""Copernicus grid store - reads fresh NRT NetCDF subsets from data/raw_copernicus.

Cached by file mtime. Used by ocean routes (chlorophyll history) and,
via the same files, the PFZ connector's own loader.
"""
from pathlib import Path
from typing import Dict, Any, List, Optional
import structlog

log = structlog.get_logger()

_CACHE: Dict[str, Any] = {"mtime": 0, "ds": None, "path": None}


def _grid_path() -> Optional[Path]:
    here = Path(__file__).resolve()
    for cand in [
        here.parents[3] / "data" / "raw_copernicus" / "mumbai_chl_fresh.nc",
        Path(r"D:\Foram_TP\ORCA\data\raw_copernicus\mumbai_chl_fresh.nc"),
    ]:
        if cand.exists():
            return cand
    return None


def chl_series(latitude: float, longitude: float) -> List[Dict[str, Any]]:
    """Daily chlorophyll at nearest 0.25deg cell, Sep 2026 fresh grid."""
    import numpy as _np
    fp = _grid_path()
    if fp is None:
        return []
    try:
        mt = fp.stat().st_mtime
        if _CACHE["ds"] is None or _CACHE["mtime"] != mt or _CACHE["path"] != str(fp):
            import xarray as _xr
            if _CACHE["ds"] is not None:
                try:
                    _CACHE["ds"].close()
                except Exception:
                    pass
            ds = _xr.open_dataset(str(fp))
            _CACHE.update({"mtime": mt, "ds": ds, "path": str(fp)})
        ds = _CACHE["ds"]
        arr = ds["chl"]
        if "depth" in arr.dims:
            arr = arr.isel(depth=0)
        lats = ds.latitude.values
        lons = ds.longitude.values
        i = int(_np.argmin(_np.abs(lats - latitude)))
        j = int(_np.argmin(_np.abs(lons - longitude)))
        out = []
        for t in range(arr.sizes["time"]):
            v = arr.values[t, i, j]
            try:
                bad = bool(_np.isnan(v))
            except Exception:
                bad = v is None
            if bad:
                # widen search for a water cell near this coast point
                found = None
                for r in (1, 2, 3):
                    try:
                        with _np.errstate(invalid="ignore"):
                            m = _np.nanmean(arr.values[t, max(0, i - r):i + r + 1, max(0, j - r):j + r + 1])
                        if not _np.isnan(m):
                            found = float(m)
                            break
                    except Exception:
                        pass
                if found is None:
                    continue
                v = found
            out.append({"observation_time": str(ds.time.values[t])[:10] + "T12:00:00+00:00",
                        "chlorophyll": round(float(v), 4)})
        return out
    except Exception as e:
        log.warning("chl_series_failed", error=str(e))
        return []
