"""Copernicus grid store - reads fresh NRT NetCDF subsets from data/raw_copernicus.

Cached by file mtime. Used by ocean routes (chlorophyll history) and,
via the same files, the PFZ connector's own loader.
"""
from pathlib import Path
from typing import Dict, Any, List, Optional
import structlog

log = structlog.get_logger()

_CACHE: Dict[str, Any] = {"mtime": 0, "ds": None, "path": None}
_SST_CACHE: Dict[str, Any] = {"mtime": 0, "ds": None, "path": None}


def _grid_file(name: str) -> Optional[Path]:
    here = Path(__file__).resolve()
    for cand in [
        here.parents[3] / "data" / "raw_copernicus" / name,
        Path(r"D:\Foram_TP\ORCA\data\raw_copernicus") / name,
    ]:
        if cand.exists():
            return cand
    return None


def _grid_path() -> Optional[Path]:
    return _grid_file("mumbai_chl_fresh.nc")


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


def _load_sst():
    """Fresh NRT SST grid (phy hourly thetao, 0.083deg), cached by mtime."""
    import xarray as _xr
    fp = _grid_file("mumbai_sst_fresh.nc")
    if fp is None:
        return None
    mt = fp.stat().st_mtime
    if _SST_CACHE["ds"] is None or _SST_CACHE["mtime"] != mt:
        if _SST_CACHE["ds"] is not None:
            try:
                _SST_CACHE["ds"].close()
            except Exception:
                pass
        ds = _xr.open_dataset(str(fp))
        _SST_CACHE.update({"mtime": mt, "ds": ds})
    return _SST_CACHE["ds"]


def grid_cells(kind: str, bbox, max_cells: int = 300):
    """Full spatial grid for map layers. kind: 'sst' | 'chl'.

    Latest time slice, strided to max_cells. Returns
    [{lat, lon, value, time}]. Values are real NetCDF cells, land masked.
    """
    import numpy as _np
    min_lon, min_lat, max_lon, max_lat = bbox
    try:
        if kind == "sst":
            ds = _load_sst()
            var = "thetao"
        else:
            fp = _grid_path()
            if fp is None:
                return [], None
            mt = fp.stat().st_mtime
            if _CACHE["ds"] is None or _CACHE["mtime"] != mt:
                import xarray as _xr
                if _CACHE["ds"] is not None:
                    try:
                        _CACHE["ds"].close()
                    except Exception:
                        pass
                _CACHE.update({"mtime": mt, "ds": _xr.open_dataset(str(fp))})
            ds = _CACHE["ds"]
            var = "chl"
        if ds is None:
            return [], None
        arr = ds[var]
        if "depth" in arr.dims:
            arr = arr.isel(depth=0)
        arr = arr.isel(time=-1)
        tdate = str(ds.time.values[-1])[:16]
        lats = ds.latitude.values
        lons = ds.longitude.values
        in_lat = [i for i, la in enumerate(lats) if min_lat <= la <= max_lat]
        in_lon = [j for j, lo in enumerate(lons) if min_lon <= lo <= max_lon]
        if not in_lat or not in_lon:
            return [], tdate
        stride = max(1, int((len(in_lat) * len(in_lon) / max_cells) ** 0.5))
        cells = []
        for ii in range(0, len(in_lat), stride):
            for jj in range(0, len(in_lon), stride):
                i, j = in_lat[ii], in_lon[jj]
                v = arr.values[i, j]
                try:
                    bad = bool(_np.isnan(v))
                except Exception:
                    bad = v is None
                if bad:
                    continue
                cells.append({"lat": round(float(lats[i]), 4), "lon": round(float(lons[j]), 4),
                              "value": round(float(v), 3)})
        return cells, tdate
    except Exception as e:
        log.warning("grid_cells_failed", kind=kind, error=str(e))
        return [], None
