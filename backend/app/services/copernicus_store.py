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
_CUR_CACHE: Dict[str, Any] = {"mtime": 0, "ds": None, "path": None}
_WAV_CACHE: Dict[str, Any] = {"mtime": 0, "ds": None, "path": None}


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


def _load_currents():
    """Fresh NRT currents grid (phy hourly uo/vo, 0.083deg), cached by mtime."""
    import xarray as _xr
    fp = _grid_file("mumbai_currents_fresh.nc")
    if fp is None:
        return None
    mt = fp.stat().st_mtime
    if _CUR_CACHE["ds"] is None or _CUR_CACHE["mtime"] != mt:
        if _CUR_CACHE["ds"] is not None:
            try:
                _CUR_CACHE["ds"].close()
            except Exception:
                pass
        ds = _xr.open_dataset(str(fp))
        _CUR_CACHE.update({"mtime": mt, "ds": ds})
    return _CUR_CACHE["ds"]


def _load_waves():
    """Fresh NRT wave grid (WAM VHM0/VTM02/VMDR, 0.083deg), cached by mtime."""
    import xarray as _xr
    fp = _grid_file("mumbai_waves_fresh.nc")
    if fp is None:
        return None
    mt = fp.stat().st_mtime
    if _WAV_CACHE["ds"] is None or _WAV_CACHE["mtime"] != mt:
        if _WAV_CACHE["ds"] is not None:
            try:
                _WAV_CACHE["ds"].close()
            except Exception:
                pass
        ds = _xr.open_dataset(str(fp))
        _WAV_CACHE.update({"mtime": mt, "ds": ds})
    return _WAV_CACHE["ds"]


def waves_cells(bbox, max_cells: int = 280):
    """Wave field for the map - height + period + direction, latest time, land masked."""
    import numpy as _np
    min_lon, min_lat, max_lon, max_lat = bbox
    try:
        ds = _load_waves()
        if ds is None:
            return [], None
        # latest 3-hour slot is the most recent valid; WAV is PT3H
        arr_h = ds["VHM0"].isel(time=-1)
        arr_p = ds["VTM02"].isel(time=-1) if "VTM02" in ds.data_vars else None
        arr_d = ds["VMDR"].isel(time=-1) if "VMDR" in ds.data_vars else None
        tdate = str(ds.time.values[-1])[:16]
        lats, lons = ds.latitude.values, ds.longitude.values
        in_lat = [i for i, la in enumerate(lats) if min_lat <= la <= max_lat]
        in_lon = [j for j, lo in enumerate(lons) if min_lon <= lo <= max_lon]
        if not in_lat or not in_lon:
            return [], tdate
        stride = max(1, int((len(in_lat) * len(in_lon) / max_cells) ** 0.5))
        cells = []
        for ii in range(0, len(in_lat), stride):
            for jj in range(0, len(in_lon), stride):
                i, j = in_lat[ii], in_lon[jj]
                h = arr_h.values[i, j]
                try:
                    if _np.isnan(h):
                        continue
                except Exception:
                    if h is None:
                        continue
                d = {"lat": round(float(lats[i]), 4), "lon": round(float(lons[j]), 4),
                     "height": round(float(h), 2)}
                if arr_p is not None:
                    try:
                        d["period"] = round(float(arr_p.values[i, j]), 1) if not _np.isnan(arr_p.values[i, j]) else None
                    except Exception:
                        d["period"] = None
                if arr_d is not None:
                    try:
                        d["direction"] = round(float(arr_d.values[i, j]), 0) if not _np.isnan(arr_d.values[i, j]) else None
                    except Exception:
                        d["direction"] = None
                cells.append(d)
        return cells, tdate
    except Exception as e:
        log.warning("waves_cells_failed", error=str(e))
        return [], None


def currents_cells(bbox, max_cells: int = 280):
    """Currents vectors for the streamlines layer.

    Latest hour slice, strided to max_cells. Returns
    [{lat, lon, uo, vo, speed, time}]. Land masked; one vector per cell.
    """
    import math as _math
    import numpy as _np
    min_lon, min_lat, max_lon, max_lat = bbox
    try:
        ds = _load_currents()
        if ds is None:
            return [], None
        tdate = str(ds.time.values[-1])[:16]
        lats = ds.latitude.values
        lons = ds.longitude.values
        in_lat = [i for i, la in enumerate(lats) if min_lat <= la <= max_lat]
        in_lon = [j for j, lo in enumerate(lons) if min_lon <= lo <= max_lon]
        if not in_lat or not in_lon:
            return [], tdate
        stride = max(1, int((len(in_lat) * len(in_lon) / max_cells) ** 0.5))
        uo_arr = ds["uo"].isel(depth=0, time=-1) if "depth" in ds["uo"].dims else ds["uo"].isel(time=-1)
        vo_arr = ds["vo"].isel(depth=0, time=-1) if "depth" in ds["vo"].dims else ds["vo"].isel(time=-1)
        cells = []
        for ii in range(0, len(in_lat), stride):
            for jj in range(0, len(in_lon), stride):
                i, j = in_lat[ii], in_lon[jj]
                uo, vo = uo_arr.values[i, j], vo_arr.values[i, j]
                try:
                    if _np.isnan(uo) or _np.isnan(vo):
                        continue
                except Exception:
                    if uo is None or vo is None:
                        continue
                sp = float(_math.hypot(float(uo), float(vo)))
                cells.append({"lat": round(float(lats[i]), 4), "lon": round(float(lons[j]), 4),
                              "uo": round(float(uo), 3), "vo": round(float(vo), 3),
                              "speed": round(sp, 3)})
        return cells, tdate
    except Exception as e:
        log.warning("currents_cells_failed", error=str(e))
        return [], None


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
